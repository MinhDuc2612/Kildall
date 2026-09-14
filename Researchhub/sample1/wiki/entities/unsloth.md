# Unsloth

A quantization/tooling group whose Dynamic v3.0 GGUF quantization method selectively adjusts bit-depth per layer (quality-sensitive layers keep more bits) rather than applying one uniform bit-depth. Qwen3.8-27B was the flagship model used to demonstrate Dynamic v3.0, with over 5.1 million downloads of its quants in the first 5 days. Unsloth's own hardware guidance for Qwen3.8-27B (4-bit needs 16–19GB, 2-bit needs 9–11GB combined VRAM/RAM) matched the source article's numbers when cross-checked.

## Mentioned in
- [Qwen 3.8 HW Mini](../../OrbiLLM/Hardware/qwen%203.8%20hw%20mini.md)
