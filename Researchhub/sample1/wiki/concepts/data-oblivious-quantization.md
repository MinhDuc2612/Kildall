# Data-oblivious quantization

TurboQuant's core algorithm (Google Research, arXiv:2504.19874, ICLR 2026): rotate a vector randomly so its coordinates hit a known statistical distribution, then apply precomputed Lloyd-Max scalar quantization — compressing to 2-4 bits/value with no training or calibration step required. In the proposed 3.5T-model workflow, this "no calibration" property matters specifically at scale, since calibration-based quantization (the kind standard PTQ methods need) would be expensive to run across an enormous expert pool.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
