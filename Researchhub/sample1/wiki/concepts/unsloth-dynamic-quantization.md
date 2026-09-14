# Unsloth Dynamic quantization (v3.0)

A GGUF quantization method that selectively adjusts bit-depth per layer rather than applying one uniform bit-depth across a model — quality-sensitive layers (e.g. output/embedding) keep more bits, less sensitive layers get compressed harder, tuned per model. Qwen3.8-27B was the flagship model used to demonstrate this method, with over 5.1 million quant downloads in its first 5 days. Analogous in spirit — non-uniform treatment of different parts of the model — to Kimi K3's trunk-resident/expert-streamed split, but precision-driven rather than routing-driven.

## Mentioned in
- [Qwen 3.8 HW Mini](../../OrbiLLM/Hardware/qwen%203.8%20hw%20mini.md)
