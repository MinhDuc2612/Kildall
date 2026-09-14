# Extreme sub-2-bit quantization

Pushing weight quantization below GGUF's usual practical floor of ~2 bits/weight — Mach-1 Additive's headline technique, compressing a 35B-parameter model to 1.7 bits/weight (a 7GB file) using purpose-built compression plus custom decode-during-compute Metal kernels, rather than standard post-training GGUF quantization. Getting usable quality this low likely implies retraining/calibration specific to the vendor's own pipeline; Mach-1's exact training methodology was not independently confirmed. Stacks with MoE sparsity when the underlying model is MoE (as Mach-1 Additive is).

## Mentioned in
- [Mach 1 HW Mini](../../OrbiLLM/Hardware/mach%201%20hw%20mini.md)
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
