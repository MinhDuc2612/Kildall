# Flash Attention

A fused attention kernel (`-fa`/`--flash-attn` in llama.cpp) that computes attention without materializing the full quadratic attention matrix in memory, cutting both memory use and compute time for the attention step specifically, with no quality tradeoff (mathematically equivalent, just fused differently). Defaults to `auto`; worth explicitly forcing on and confirming it's active, since a silent fallback to off re-introduces the memory cost it exists to avoid.

## Mentioned in
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
