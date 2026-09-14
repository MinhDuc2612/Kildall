# Turbo Fieldfare

A real project (`drumih/turbo-fieldfare`, Apache-2.0, first commit 2026-07-17) — a native Swift + Metal inference runtime that runs Google DeepMind's Gemma 4 26B-A4B MoE model in ~2GB of active RAM on any Apple Silicon Mac with 8GB+ RAM, keeping only a small shared core plus FP16 KV cache resident and streaming routed experts from a custom `.gturbo` format through a 16-slot-per-layer LFU cache. Reported throughput: 4–6 tok/s on M1/M2 MacBook Air, 25–36 tok/s on M4 Pro/M5. It is hard-pinned to one exact model and quantization, so its value in the proposed 3.5T-model workflow is architectural (proof the pattern works well on Apple Silicon) rather than as a drop-in tool.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
