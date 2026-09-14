# Speculative decoding

Running a small, fast "draft" model to guess several tokens ahead, then verifying them in one batched pass with the real model (`--spec-draft-model`/`-md` in llama.cpp) — when the draft guesses right, multiple tokens come at roughly the cost of one full-model forward pass. A speed technique primarily, not a memory-reduction one, but it changes the practical calculus of running a heavily-quantized big model. Mach-1's docs reference a similar mode reaching ~163 tok/s versus ~117 tok/s single-stream (unverified figure).

## Mentioned in
- [HW Mini — Combined Guide](../../OrbiLLM/Hardware/hwmini.md)
- [Mach 1 HW Mini](../../OrbiLLM/Hardware/mach%201%20hw%20mini.md)
