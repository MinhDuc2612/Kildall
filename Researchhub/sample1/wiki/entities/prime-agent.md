# Prime Agent

An open-source (MIT-licensed) "Self-Improving RLM Agent," github.com/PrimeIntellect-ai/prime-agent, released by Prime Intellect (announced 2026-08-05), built on top of "pi," a minimal agent harness by Mario Zechner. Built on two abstractions: a Recursive Language Model (the model's tool is a persistent IPython REPL; context is a Python variable) and a Continual Harness (a self-improvement mechanism where the agent's operating state — prompts, sub-agent specs, skills, memory — is CRUD-able, with an immutable base system prompt and snapshotted rollback). Reported 95.5% Best@1 on ARC-AGI-3 with Opus 5, above the benchmark's human-expert baseline of 95.4%. Explicitly not a security sandbox.

## Mentioned in
- [LLM Self-Improve](../../OrbiLLM/LLMtrain/LLM%20self-improve.md)
