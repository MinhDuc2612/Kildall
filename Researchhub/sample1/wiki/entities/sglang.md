# SGLang (SGL)

A high-performance LLM serving framework, GPU-first by default (NVIDIA CUDA), known for RadixAttention. SGLang ships an official Apple Silicon Metal path via Apple's MLX framework (`SGLANG_USE_MLX=1`), measured at 3.9–4.6x higher throughput than the naive Mac PyTorch-MPS path in one benchmark — proposed as the serving/scheduling layer for repeated or agentic prompts in the 3.5T-model workflow.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
