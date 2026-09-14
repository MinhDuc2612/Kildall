# MXFP4 (Microscaling FP4)

A 4-bit floating-point format with per-block scaling that Kimi K3 ships its weights in (paired with MXFP8 activations), trained via quantization-aware training from the SFT stage onward — meaning the low-bit representation was trained to be tolerated, not bolted on as a lossy afterthought post-training. Contrasted with GGUF quantization (typically applied post-training by third parties for dense models like Qwen3.8-27B).

## Mentioned in
- [Kimi K3 HW Mini](../../OrbiLLM/Hardware/kimi%20k3%20hw%20mini.md)
- [Qwen 3.8 HW Mini](../../OrbiLLM/Hardware/qwen%203.8%20hw%20mini.md)
