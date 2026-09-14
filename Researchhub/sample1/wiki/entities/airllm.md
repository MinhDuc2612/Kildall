# AirLLM

A layer-by-layer streaming technique: load one transformer layer's weights from disk, run it, discard it, load the next — demonstrated reducing a 70B dense model's active memory footprint to roughly the size of one layer (~1.6GB) without quantization. Described as the precursor pattern to what Colibri/Turbo Fieldfare do for MoE models, but streams whole layers rather than individual experts, making it far less efficient for a sparse MoE model.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
