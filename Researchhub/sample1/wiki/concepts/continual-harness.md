# Continual Harness

Prime Agent's self-improvement mechanism, narrower and more controlled than "self-improvement" might suggest. The harness's operating state is formalized as H = (ρ, G, K, M) — prompts, sub-agent specs, skills, and memory — all CRUD-able mid-task. Running `/refine` reviews the agent's own trajectory and applies the smallest relevant edit to one of those four components. Two guardrails: the immutable base system prompt is never touched by `/refine`, and every refinement is snapshotted for rollback by ID. This is scaffold-level self-improvement (the harness's operating state changes), not weight-level self-improvement (the underlying model is untouched) — a meaningfully safer design point than open-ended source-code-rewriting agents like Darwin Gödel Machine.

## Mentioned in
- [LLM Self-Improve](../../OrbiLLM/LLMtrain/LLM%20self-improve.md)
