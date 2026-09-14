# KV cache quantization

Quantizing the running memory of every token's attention keys/values (`-ctk`/`-ctv` in llama.cpp) to q8_0, q4_0, q4_1, iq4_nl, q5_0, or q5_1 instead of the default f16 — shrinks a memory cost that grows linearly with context length, independent of the model weights' own quantization. On long-context sessions the KV cache can rival the model's own size, making this the single highest-leverage fix for OOM specifically on long prompts (a distinct failure mode from "model doesn't fit at all"). KIVI is a specific, well-established asymmetric (per-channel for keys, per-token for values) 2-bit KV-quantization scheme in the same family.

## Mentioned in
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
