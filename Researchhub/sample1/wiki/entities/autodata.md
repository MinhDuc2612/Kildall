# Autodata

A Meta FAIR framework (paper: "Autodata: An agentic data scientist to create high quality synthetic data," arXiv:2606.25996, June 2026, Jason Weston's team) where an AI agent plays the role of a data scientist — generating synthetic training/eval data, testing whether it's actually useful, and revising its own generation strategy based on results, a closed loop rather than one-shot generation. Its concrete instantiation, Agentic Self-Instruct, uses four coordinated LLM subagents (Challenger, weak solver, strong solver, Verifier/Judge) under one orchestrator, accepting an example only if the strong solver clearly succeeds and the weak solver clearly struggles. On CS-paper-derived QA pairs this raised the weak/strong performance gap from 1.9 points (standard Self-Instruct baseline) to 34 points, and training Qwen 3.5 on the resulting data outperformed training on the standard synthetic dataset.

## Mentioned in
- [LLM-autotrain](../../OrbiLLM/LLMtrain/LLM-autotrain.md)
