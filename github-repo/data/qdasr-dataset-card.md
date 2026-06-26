# Quantized Deviations in AI Self-Reference (QDASR)

## Dataset Description

### Summary

QDASR collects measured deviation patterns when AI systems engage in self-reference tasks. The core finding: self-reference deviations form discrete staircases — not continuous noise — characterized by the **LXH interval Δₓ** (Lin Xiaohei, 2026).

### Structure

Each sample:
- `model_name`: Model identifier (e.g., "llama-3.3-70b")
- `task`: The task prompt used
- `original_output`: Model output without self-reference context
- `regenerated_output`: Model output after observing its own output
- `deviation`: Measured difference (normalized edit distance, 0-1)
- `trial_number`: Trial index within the experiment
- `temperature`: Generation temperature
- `architecture`: Model architecture family
- `lxh_interval_estimated`: Estimated Δₓ for this model (if computed across trials)

### Usage

```python
from datasets import load_dataset

dataset = load_dataset("samforce/qdasr")
# Analyze deviation histogram for staircase pattern
```

### Citation

```bibtex
@dataset{xiaohei2026qdasr,
  title={Quantized Deviations in AI Self-Reference (QDASR)},
  author={Xiaohei, Lin},
  year={2026},
  note={Dataset supporting the Dequantized Discrete Staircase framework},
  url={https://huggingface.co/datasets/samforce/qdasr}
}
```

### License

CC BY 4.0 — use freely, cite accordingly.
