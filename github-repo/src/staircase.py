"""
Staircase Analysis Tools
========================
Visualization and analysis utilities for DDS measurements.
Generates staircase plots, peak histograms, and convergence diagnostics.
"""

import json
from pathlib import Path
from datetime import datetime
from measure import DDSResult, _estimate_delta_x, _find_histogram_peaks


def plot_staircase(result: DDSResult, output_path: str = None) -> str:
    """
    Generate a staircase plot in HTML (self-contained, no deps).
    Returns HTML string.
    """
    deviations = result.deviations
    sorted_devs = sorted(deviations)

    # Build data for JS
    data_json = json.dumps({
        "deviations": deviations,
        "delta_x": result.delta_x,
        "k_max": result.k_max,
        "peaks": [round(p, 4) for p in sorted(result.peaks)],
        "task": result.task[:80],
        "trials": result.trial_count,
    })

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>DDS Staircase — {result.task[:40]}</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #0d1117; color: #c9d1d9; }}
  h1 {{ color: #58a6ff; }}
  .stat {{ display: inline-block; margin: 10px 20px 10px 0; }}
  .stat-label {{ font-size: 12px; color: #8b949e; text-transform: uppercase; }}
  .stat-value {{ font-size: 28px; font-weight: bold; color: #58a6ff; }}
  canvas {{ display: block; margin: 20px 0; background: #161b22; border-radius: 8px; }}
  .note {{ color: #8b949e; font-size: 13px; margin-top: 30px; border-top: 1px solid #30363d; padding-top: 15px; }}
</style>
</head>
<body>
<h1>Dequantized Discrete Staircase</h1>
<p style="color:#8b949e">Task: {result.task[:100]}</p>

<div>
  <div class="stat"><div class="stat-label">LXH Interval Δₓ</div><div class="stat-value">{result.delta_x:.4f}</div></div>
  <div class="stat"><div class="stat-label">Max Depth k_max</div><div class="stat-value">{result.k_max}</div></div>
  <div class="stat"><div class="stat-label">Trials</div><div class="stat-value">{result.trial_count}</div></div>
  <div class="stat"><div class="stat-label">Peaks</div><div class="stat-value">{len(result.peaks)}</div></div>
</div>

<canvas id="histogram" width="850" height="300"></canvas>
<canvas id="staircase" width="850" height="200"></canvas>
<canvas id="convergence" width="850" height="200"></canvas>

<script>
const data = {data_json};

// --- Histogram ---
(function() {{
  const canvas = document.getElementById('histogram');
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  const padding = {{top: 20, right: 30, bottom: 40, left: 50}};
  const pw = w - padding.left - padding.right;
  const ph = h - padding.top - padding.bottom;

  // Build bins
  const n_bins = Math.min(50, Math.ceil(Math.sqrt(data.deviations.length)));
  const minD = Math.min(...data.deviations);
  const maxD = Math.max(...data.deviations);
  const binW = (maxD - minD) / n_bins || 0.001;
  const bins = new Array(n_bins).fill(0);
  data.deviations.forEach(d => {{
    const idx = Math.min(Math.floor((d - minD) / binW), n_bins - 1);
    if (idx >= 0) bins[idx]++;
  }});
  const maxBin = Math.max(...bins);

  // Axes
  ctx.strokeStyle = '#30363d';
  ctx.fillStyle = '#8b949e';
  ctx.font = '11px monospace';
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + ph);
  ctx.lineTo(padding.left + pw, padding.top + ph);
  ctx.stroke();

  // Bars
  bins.forEach((count, i) => {{
    const x = padding.left + (i / n_bins) * pw;
    const barW = Math.max(1, pw / n_bins - 1);
    const barH = (count / maxBin) * ph;
    const y = padding.top + ph - barH;

    // Color: blue for bars near peaks, gray otherwise
    const center = minD + (i + 0.5) * binW;
    const nearPeak = data.peaks.some(p => Math.abs(center - p) < binW * 1.5);
    ctx.fillStyle = nearPeak ? 'rgba(88,166,255,0.7)' : 'rgba(48,54,61,0.5)';
    ctx.fillRect(x, y, barW, barH);
  }});

  // Peak markers
  data.peaks.forEach(p => {{
    const x = padding.left + ((p - minD) / (maxD - minD)) * pw;
    ctx.fillStyle = '#58a6ff';
    ctx.beginPath();
    ctx.arc(x, padding.top + ph - ((bins[Math.floor((p-minD)/binW)] || 0) / maxBin) * ph - 8, 4, 0, Math.PI*2);
    ctx.fill();
    ctx.fillText(p.toFixed(3), x - 15, padding.top + ph + 15);
  }});

  // Labels
  ctx.fillStyle = '#8b949e';
  ctx.font = '11px sans-serif';
  ctx.fillText('Deviation (D)', padding.left + pw/2 - 30, padding.top + ph + 30);
  ctx.fillText('0', padding.left - 30, padding.top + ph);
  ctx.fillText(maxD.toFixed(2), padding.left - 30, padding.top + 5);
}})();

// --- Staircase cumulative ---
(function() {{
  const canvas = document.getElementById('staircase');
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  const padding = {{top: 20, right: 30, bottom: 40, left: 50}};
  const pw = w - padding.left - padding.right;
  const ph = h - padding.top - padding.bottom;

  const sorted = [...data.deviations].sort((a,b) => a-b);
  const steps = [];
  const dx = data.delta_x || 0.001;
  for (let d = 0; d <= Math.max(...sorted); d += dx) {{
    steps.push({{x: d, y: sorted.filter(v => v <= d).length}});
  }}

  ctx.strokeStyle = '#30363d';
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + ph);
  ctx.lineTo(padding.left + pw, padding.top + ph);
  ctx.stroke();

  ctx.strokeStyle = '#58a6ff';
  ctx.lineWidth = 2;
  ctx.beginPath();
  steps.forEach((s, i) => {{
    const x = padding.left + (s.x / (steps[steps.length-1]?.x || 1)) * pw;
    const y = padding.top + ph - (s.y / data.deviations.length) * ph;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }});
  ctx.stroke();

  ctx.fillStyle = '#8b949e';
  ctx.font = '11px sans-serif';
  ctx.fillText('Deviation', padding.left + pw/2 - 20, padding.top + ph + 30);
  ctx.fillText('Cumulative Count', padding.left - 45, padding.top - 5);
}})();

// --- Convergence (running k_max) ---
(function() {{
  const canvas = document.getElementById('convergence');
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  const padding = {{top: 20, right: 30, bottom: 40, left: 50}};
  const pw = w - padding.left - padding.right;
  const ph = h - padding.top - padding.bottom;

  const runningKmax = [];
  let maxSoFar = 0;
  const dx = data.delta_x || 0.001;
  data.deviations.forEach((d, i) => {{
    maxSoFar = Math.max(maxSoFar, d);
    runningKmax.push({{x: i, y: Math.round(maxSoFar / dx)}});
  }});

  ctx.strokeStyle = '#30363d';
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + ph);
  ctx.lineTo(padding.left + pw, padding.top + ph);
  ctx.stroke();

  ctx.strokeStyle = '#3fb950';
  ctx.lineWidth = 2;
  ctx.beginPath();
  runningKmax.forEach((p, i) => {{
    const x = padding.left + (p.x / data.deviations.length) * pw;
    const y = padding.top + ph - (p.y / (data.k_max || 1)) * ph;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }});
  ctx.stroke();

  ctx.fillStyle = '#8b949e';
  ctx.font = '11px sans-serif';
  ctx.fillText('Trial #', padding.left + pw/2 - 20, padding.top + ph + 30);
  ctx.fillText('k_max', padding.left - 30, padding.top - 5);
}})();
</script>

<p class="note">
  Measured using the DDS protocol (Lin Xiaohei, 2026).<br>
  Δₓ (LXH interval) = minimum self-difference resolvable by this system.<br>
  k_max = max staircase depth before frame saturation.
</p>
</body>
</html>"""
    
    if output_path:
        Path(output_path).write_text(html, encoding='utf-8')

    return html


def detect_staircase_pattern(deviations: list[float], min_confidence: float = 0.3) -> dict:
    """
    Quick check: does this data show staircase pattern?
    Returns dict with has_staircase (bool), confidence (float), and explanation (str).
    """
    n = len(deviations)
    if n < 20:
        return {"has_staircase": False, "confidence": 0.0, 
                "explanation": "Too few trials (< 20) for reliable detection."}

    peaks, _ = _find_histogram_peaks(deviations)

    if len(peaks) < 2:
        return {"has_staircase": False, "confidence": 0.1,
                "explanation": "Only one peak detected. Increase trial count or try different task."}

    dx = _estimate_delta_x(peaks)
    if dx < 1e-9:
        return {"has_staircase": False, "confidence": 0.0,
                "explanation": "Peaks too close together — no quantization detected."}

    # Check if peaks are evenly spaced
    sorted_peaks = sorted(peaks)
    gaps = [sorted_peaks[i+1] - sorted_peaks[i] for i in range(len(sorted_peaks)-1)]
    gap_std = __import__('statistics').stdev(gaps) if len(gaps) > 1 else 0
    gap_mean = sum(gaps) / len(gaps)
    cv = gap_std / gap_mean if gap_mean > 0 else float('inf')

    if cv < 0.3:
        confidence = 0.9
        explanation = f"Strong staircase pattern: {len(peaks)} evenly-spaced peaks, Δₓ ≈ {dx:.4f}"
    elif cv < 0.6:
        confidence = 0.6
        explanation = f"Moderate staircase pattern: {len(peaks)} peaks with some spacing variation"
    else:
        confidence = 0.3
        explanation = f"Weak staircase signal: peak spacing is irregular (CV={cv:.2f})"

    has_staircase = confidence >= min_confidence

    return {
        "has_staircase": has_staircase,
        "confidence": confidence,
        "delta_x": dx,
        "peak_count": len(peaks),
        "explanation": explanation,
    }


# --- Batch comparison ---

def compare_models(results: dict[str, "DDSResult"]) -> str:
    """Compare DDS results across multiple models."""
    lines = ["Model Comparison — LXH Interval (Δₓ)", "=" * 50]
    for name, result in results.items():
        lines.append(f"{name:20s}: Δₓ={result.delta_x:.4f}, k_max={result.k_max}")
    return "\n".join(lines)


if __name__ == "__main__":
    print("Staircase Analysis Tools v1.0")
    print("Usage: from staircase import plot_staircase, detect_staircase_pattern")
