# GGUF quantization

llama.cpp's model-file format, supporting per-tensor quantization at multiple bit-depths (2-bit through 8-bit, plus native BF16), the primary hardware-minimization lever for dense models with no MoE sparsity to exploit. For Qwen3.8-27B, going from BF16 (~55.5GB) to 4-bit cuts footprint to ~17GB (~3.2x reduction) and to 2-bit cuts it to ~9-10GB (~5.5x reduction), at a real quality/speed cost that grows sharply below 2-bit. Distinct from Kimi K3's quantization-aware-from-training MXFP4 format — GGUF quants are typically post-training quantization applied afterward by third parties (e.g. Unsloth, bartowski) using calibration data ("imatrix").

## Mentioned in
- [Qwen 3.8 HW Mini](../../OrbiLLM/Hardware/qwen%203.8%20hw%20mini.md)
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
- [Mach 1 HW Mini](../../OrbiLLM/Hardware/mach%201%20hw%20mini.md)
