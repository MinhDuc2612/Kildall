# Recursive Language Model (RLM)

Prime Agent's core abstraction: instead of a fixed tool-calling schema, the model's only real "tool" is a persistent IPython REPL. Context becomes a Python variable the model can slice, store, and pass around ("prompt-as-a-variable"), and calling a sub-agent is just a function call (`rlm(...)`) inside that REPL rather than a separate orchestration layer — letting the agent treat very long sessions as a programming problem, offloading history into variables instead of holding everything in the active context window.

## Mentioned in
- [LLM Self-Improve](../../OrbiLLM/LLMtrain/LLM%20self-improve.md)
