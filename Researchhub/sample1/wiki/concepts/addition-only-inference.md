# "Addition-only" inference

An inference technique where a model performs matrix operations without ever multiplying by a weight, replacing multiplication with addition — the same family as BitNet-style ternary-weight models, which use {-1, 0, +1} weights specifically so multiply-accumulate degenerates into add/subtract. Suggested by Mach-1 Additive's name and a company social-media post, but explicitly flagged as an inference from naming and an unverified social post, not confirmed against the model's actual architecture — reported as an unverified claim, not established fact.

## Mentioned in
- [Mach 1 HW Mini](../../OrbiLLM/Hardware/mach%201%20hw%20mini.md)
