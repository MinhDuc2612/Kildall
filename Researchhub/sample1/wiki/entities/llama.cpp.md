# llama.cpp

The best-known general local-LLM inference engine (C/C++, minimal dependencies), running on x86 CPUs, ARM CPUs, Apple Silicon (via Metal), NVIDIA (CUDA), AMD (ROCm), and Vulkan hardware. Works with GGUF-format quantized models, supports partial GPU-layer offload (`-ngl`) and mmap-based disk-backed loading; its server docs are the primary source for the KV-cache-quantization, Flash Attention, load-mode, speculative-decoding, and context/batch-sizing flags catalogued in the combined hardware-minimization guide. Rated the most Mac-proven tool among the 3.5T-model workflow's eight surveyed tools.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
- [Qwen 3.8 HW Mini](../../OrbiLLM/Hardware/qwen%203.8%20hw%20mini.md)
