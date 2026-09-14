# Fused decode-in-GEMV Metal kernels

Mach Engine's technique for running Mach-1 Additive's 1.7-bit weights on Apple Silicon: custom Metal (Apple's GPU compute API) kernels fused directly into the matrix-vector multiply step (GEMV, the core operation in autoregressive decoding), decoding quantized weights during the multiply-accumulate operation itself so no full-precision or even 4-bit intermediate copy is ever materialized in memory. A tighter, purpose-built version of what generic llama.cpp does for GGUF models.

## Mentioned in
- [Mach 1 HW Mini](../../OrbiLLM/Hardware/mach%201%20hw%20mini.md)
