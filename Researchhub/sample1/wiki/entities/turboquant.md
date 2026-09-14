# TurboQuant

Two distinct things share this name: (1) a Google Research paper (arXiv:2504.19874, ICLR 2026) describing a data-oblivious vector/weight quantizer that rotates a vector randomly then applies precomputed Lloyd-Max scalar quantization, no calibration needed, compressing to 2–4 bits/value; and (2) independent GitHub implementations (`0xSero/turboquant`, `cksac/turboquant-model`) of that algorithm as a KV-cache quantization tool, confirmed CUDA/vLLM-only with no Apple Silicon path. In the proposed 3.5T-model workflow, only the underlying algorithm (not the existing CUDA-only code) is usable, for compressing routed-expert shards before writing them to disk.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
