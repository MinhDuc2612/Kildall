# Colibri

A from-scratch C inference engine (`JustVugg/colibri`) built to run huge MoE models (its own stated range: 744B–2.8T parameters) on consumer hardware by treating disk, RAM, and VRAM as one memory hierarchy — keeping dense/shared layers resident in RAM as int4 and streaming routed experts from disk as small int4 shards, with one-layer-ahead routing prediction (self-reported ~71.6% accurate) to prefetch. The same architectural family as kimi-k3-in-c; central to the proposed 3.5T-model workflow's storage and RAM strategy.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
