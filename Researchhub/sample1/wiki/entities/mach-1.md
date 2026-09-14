# Mach-1

Syzygy Research's combined model+engine package for running a 35B-parameter model entirely on a Mac, no cloud or API key needed. Two parts: **Mach-1 Additive** (the model — a 35B-parameter MoE based on Qwen 3.6 35B, compressed to 1.7 bits/weight, a 7GB file, claimed to retain 96.3% of its unquantized teacher's performance across 12 benchmarks per Syzygy's own reporting) and **Mach Engine** (the runtime — fused decode-in-GEMV Metal kernels, OpenAI-compatible API, requires Apple Silicon + Python 3.12+). Fits on a 16GB Mac. The "addition-only"/never-multiplies-by-a-weight framing and the ~120 tok/s throughput figure are reported but explicitly unverified in the source doc.

## Mentioned in
- [Mach 1 HW Mini](../../OrbiLLM/Hardware/mach%201%20hw%20mini.md)
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
