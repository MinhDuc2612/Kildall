# RadixAttention

A radix-tree-based KV-cache reuse mechanism in SGLang that lets requests sharing a common prompt prefix (a fixed system prompt, a repeated agentic loop context) skip recomputing that prefix entirely — strong for agentic/RAG workloads with shared context, proposed as part of the compute-execution layer in the 3.5T-model workflow.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
