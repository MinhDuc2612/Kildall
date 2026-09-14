# Turbovec

A Rust (+ Python bindings) vector index (`RyanCodrai/turbovec`) implementing the TurboQuant algorithm for embeddings/RAG corpora rather than LLM weights — compresses a 10M-document, 31GB float32 corpus to 4GB (16x) and, per its own benchmarks, searches faster than FAISS. Hand-written NEON (ARM) kernels make it genuinely Apple-Silicon-friendly; has llama.cpp-compatible and Ollama-compatible modes plus LangChain/Agno integrations. Relevant to the proposed 3.5T-model workflow only if the deployment includes a retrieval/RAG layer.

## Mentioned in
- [Running a 3.5T-Parameter LLM on a Mac Mini M4](../../OrbiLLM/Hardware/3.5T%20local%20LLM%20hardware%20workflow.md)
