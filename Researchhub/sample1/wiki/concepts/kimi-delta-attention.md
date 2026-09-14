# Kimi Delta Attention (KDA)

A hybrid linear-attention mechanism in Kimi K3 (from the earlier "Kimi Linear" research, Oct 2025) that interleaves cheap linear-attention layers with periodic full-attention layers (roughly 3:1), cutting KV-cache memory by up to 75% and enabling the model's 1,048,576-token context window without full quadratic attention cost.

## Mentioned in
- [Kimi K3 HW Mini](../../OrbiLLM/Hardware/kimi%20k3%20hw%20mini.md)
