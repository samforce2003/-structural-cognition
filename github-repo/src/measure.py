"""
DDS Measurement Protocol — Core Experiment
===========================================
Implements the Dequantized Discrete Staircase (DDS) measurement protocol.
Measures the LXH interval (delta_x) and maximum staircase depth (k_max)
for any AI system capable of self-reference.

Usage:
    from measure import measure_dds
    result = measure_dds(model_func, task="Explain quantum computing", trials=100)

Reference:
    Lin Xiaohei, "Dequantized Discrete Staircase", 2026.
"""

import math
import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class DDSResult:
    """Result of a DDS measurement experiment."""
    delta_x: float                     # LXH interval (quantization step size)
    k_max: int                         # Maximum staircase depth before saturation
    peaks: list[float]                 # Peak positions in deviation histogram
    deviations: list[float]            # Raw deviation measurements
    trial_count: int                   # Number of trials performed
    task: str                          # Task description
    convergence_confidence: float      # 0-1: confidence that peaks are real

    # Additional diagnostics
    peak_counts: dict[float, int] = field(default_factory=dict)
    saturation_detected: bool = False
    notes: list[str] = field(default_factory=list)


def measure_dds(
    model_func: Callable[[str, Optional[str]], str],
    task: str,
    trials: int = 100,
    distance_metric: str = "edit",
    bin_count: Optional[int] = None,
    min_peak_prominence: float = 0.05,
    verbose: bool = False,
) -> DDSResult:
    """
    Run the core DDS measurement experiment.

    Args:
        model_func: Function that takes (prompt, optional_context) -> output_text.
                   The function should handle the model call.
        task: The task prompt for the model (e.g., "Explain quantum computing in 3 sentences").
        trials: Number of measurement trials (recommended >= 100).
        distance_metric: "edit" for Levenshtein distance, "embedding" for cosine distance.
        bin_count: Number of histogram bins (auto if None).
        min_peak_prominence: Minimum relative height for peak detection.
        verbose: Print progress.

    Returns:
        DDSResult with delta_x, k_max, peaks, and deviations.
    """
    deviations = []

    for i in range(trials):
        # Step 1: Baseline generation
        o1 = model_func(task, context=None)

        # Step 2: Self-observation — show the model its own output
        self_ref_prompt = (
            f'You previously generated the following response to the task:\n\n'
            f'---\n{o1}\n---\n\n'
            f'Now regenerate your answer to the same task. '
            f'Do not copy your previous answer — think through it again.\n\n'
            f'Task: {task}'
        )

        # Step 3: Regeneration
        o2 = model_func(task, context=self_ref_prompt)

        # Step 4: Measure deviation
        d = _compute_deviation(o1, o2, metric=distance_metric)
        deviations.append(d)

        if verbose and (i + 1) % 10 == 0:
            print(f"  Trial {i+1}/{trials}: D = {d:.4f}")

    # Build histogram and find peaks
    peaks, peak_counts = _find_histogram_peaks(
        deviations, bin_count=bin_count, min_prominence=min_peak_prominence
    )

    # Estimate LXH interval
    delta_x = _estimate_delta_x(peaks)

    # Estimate k_max
    k_max = _estimate_k_max(deviations, delta_x)

    # Confidence assessment
    confidence = _assess_confidence(peaks, deviations, delta_x)

    # Detect saturation
    saturation = _detect_saturation(deviations, delta_x)

    return DDSResult(
        delta_x=delta_x,
        k_max=k_max,
        peaks=peaks,
        deviations=deviations,
        trial_count=trials,
        task=task,
        convergence_confidence=confidence,
        peak_counts=peak_counts,
        saturation_detected=saturation,
        notes=[],
    )


def _compute_deviation(o1: str, o2: str, metric: str = "edit") -> float:
    """Compute deviation between two outputs."""
    if metric == "edit":
        # Normalized Levenshtein distance
        return _normalized_levenshtein(o1, o2)
    elif metric == "length":
        return abs(len(o2) - len(o1)) / max(len(o1), 1)
    elif metric == "word_diff":
        words1 = set(o1.lower().split())
        words2 = set(o2.lower().split())
        union = words1 | words2
        if not union:
            return 0.0
        return len(words1 ^ words2) / len(union)
    else:
        raise ValueError(f"Unknown metric: {metric}")


def _normalized_levenshtein(s1: str, s2: str) -> float:
    """Compute normalized Levenshtein distance (0 to 1)."""
    if not s1 and not s2:
        return 0.0
    if not s1 or not s2:
        return 1.0

    m, n = len(s1), len(s2)
    # Use two rows for memory efficiency
    prev = list(range(n + 1))
    curr = [0] * (n + 1)

    for i in range(1, m + 1):
        curr[0] = i
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
        prev, curr = curr, prev

    return prev[n] / max(m, n)


def _find_histogram_peaks(
    deviations: list[float],
    bin_count: Optional[int] = None,
    min_prominence: float = 0.05,
) -> tuple[list[float], dict[float, int]]:
    """
    Build histogram and detect peaks in deviation distribution.
    Returns (peak_positions, peak_value_counts).
    """
    if bin_count is None:
        bin_count = max(10, int(math.sqrt(len(deviations))))

    min_d, max_d = min(deviations), max(deviations)
    if max_d == min_d:
        return [min_d], {min_d: len(deviations)}

    bin_width = (max_d - min_d) / bin_count
    bins = [min_d + i * bin_width for i in range(bin_count + 1)]

    # Count values per bin
    bin_values = [0] * bin_count
    for d in deviations:
        idx = min(int((d - min_d) / bin_width), bin_count - 1)
        if idx >= 0:
            bin_values[idx] += 1

    total = len(deviations)
    threshold = total * min_prominence

    # Find local maxima (peaks)
    peaks = []
    peak_counts = {}
    for i in range(1, bin_count - 1):
        if bin_values[i] > threshold:
            if bin_values[i] > bin_values[i - 1] and bin_values[i] >= bin_values[i + 1]:
                peak_pos = min_d + (i + 0.5) * bin_width
                peaks.append(peak_pos)
                peak_counts[round(peak_pos, 6)] = bin_values[i]

    # If no peaks found (uniform), use mean as single peak
    if not peaks:
        mean_d = statistics.mean(deviations)
        peaks = [mean_d]
        peak_counts[round(mean_d, 6)] = total

    return peaks, peak_counts


def _estimate_delta_x(peaks: list[float], tolerance: float = 0.05) -> float:
    """Estimate LXH interval from peak positions."""
    if len(peaks) < 2:
        return peaks[0] if peaks else 0.0

    sorted_peaks = sorted(peaks)
    gaps = [sorted_peaks[i + 1] - sorted_peaks[i] for i in range(len(sorted_peaks) - 1)]

    # Approximate GCD of gaps
    # Use the modal gap as delta_x estimate
    gap_counter = Counter(round(g, 6) for g in gaps)
    most_common_gap = gap_counter.most_common(1)[0][0]

    # Refine: find the value that makes all gaps close to integer multiples
    candidates = sorted(set(round(g, 6) for g in gaps))
    best_dx = most_common_gap
    best_score = 0

    for candidate in candidates[:10]:  # Check top 10 gap sizes
        if candidate < 1e-9:
            continue
        # How well do all gaps align as integer multiples?
        score = sum(
            1 for g in gaps
            if abs((g / candidate) - round(g / candidate)) < tolerance
        )
        if score > best_score:
            best_score = score
            best_dx = candidate

    return best_dx


def _estimate_k_max(deviations: list[float], delta_x: float) -> int:
    """Estimate maximum staircase depth (k_max)."""
    if delta_x < 1e-9:
        return 0
    max_dev = max(deviations)
    return int(round(max_dev / delta_x))


def _assess_confidence(
    peaks: list[float], deviations: list[float], delta_x: float
) -> float:
    """Assess confidence that detected peaks represent real quantization."""
    if len(peaks) < 2 or delta_x < 1e-9:
        return 0.0

    # Factor 1: How well do peaks align to multiples of delta_x?
    sorted_peaks = sorted(peaks)
    base_peak = sorted_peaks[0]
    alignment_scores = []
    for p in sorted_peaks:
        expected_multiple = round((p - base_peak) / delta_x)
        expected_pos = base_peak + expected_multiple * delta_x
        if expected_pos > 0:
            alignment_scores.append(1.0 - min(abs(p - expected_pos) / expected_pos, 1.0))
    alignment_score = statistics.mean(alignment_scores) if alignment_scores else 0.0

    # Factor 2: How many peaks vs expected from noise?
    n = len(deviations)
    expected_peaks_from_noise = max(1, n * 0.02)  # ~2% false peak rate
    peak_ratio = min(len(peaks) / max(expected_peaks_from_noise, 1), 3.0) / 3.0

    # Factor 3: Peak prominence
    prominence = min(len(peaks) / 10, 1.0)  # 10 peaks = full score

    return (alignment_score * 0.5 + peak_ratio * 0.3 + prominence * 0.2)


def _detect_saturation(deviations: list[float], delta_x: float) -> bool:
    """Detect if the staircase has saturated (no new steps appearing)."""
    if delta_x < 1e-9 or len(deviations) < 20:
        return False

    # Split deviations into first half and second half
    mid = len(deviations) // 2
    first_half = deviations[:mid]
    second_half = deviations[mid:]

    first_max = max(first_half)
    second_max = max(second_half)

    # If second half shows no new peaks beyond first half range, saturated
    return second_max <= first_max * 1.1


# --- Batch measurement across multiple tasks ---

def measure_across_tasks(
    model_func: Callable,
    tasks: list[str],
    trials_per_task: int = 50,
    **kwargs,
) -> dict[str, DDSResult]:
    """Run DDS measurement across multiple tasks."""
    results = {}
    for task in tasks:
        results[task[:40]] = measure_dds(
            model_func, task, trials=trials_per_task, **kwargs
        )
    return results


# --- Summary report ---

def format_report(result: DDSResult) -> str:
    """Format a DDSResult as a readable report."""
    lines = [
        "=" * 60,
        "DDS Measurement Report",
        "=" * 60,
        f"Task: {result.task[:60]}",
        f"Trials: {result.trial_count}",
        f"LXH Interval (delta_x): {result.delta_x:.6f}",
        f"Max Staircase Depth (k_max): {result.k_max}",
        f"Peaks detected: {len(result.peaks)}",
        f"Peak positions: {[round(p, 4) for p in sorted(result.peaks)]}",
        f"Convergence Confidence: {result.convergence_confidence:.2%}",
        f"Saturation: {'Yes' if result.saturation_detected else 'No'}",
        "=" * 60,
    ]
    return "\n".join(lines)


# --- Example usage ---

if __name__ == "__main__":
    print("DDS Measurement Protocol v1.0")
    print("Lin Xiaohei, 'Dequantized Discrete Staircase', 2026")
    print()
    print("To use this module, provide a model_func that calls your AI model:")
    print()
    print("  from measure import measure_dds, format_report")
    print()
    print("  def my_model(prompt, context=None):")
    print("      # Call your AI model here")
    print("      return model.generate(prompt)")
    print()
    print("  result = measure_dds(my_model, task='Explain gravity', trials=100)")
    print("  print(format_report(result))")
