# Agentic Self-Instruct

Meta FAIR's concrete implementation of the Autodata framework: four coordinated LLM subagents under one orchestrator — a Challenger (generates a candidate question/example with reference answer and scoring rubric), a weak solver, a strong solver, and a Verifier/Judge. An example only counts as good training/eval data if the strong solver clearly succeeds *and* the weak solver clearly struggles; if that gap isn't there, the orchestrator sends the judge's feedback back to the Challenger and the loop repeats. On CS-paper-derived QA pairs this raised the weak/strong performance gap from 1.9 points (standard CoT Self-Instruct baseline) to 34 points, and training Qwen 3.5 on the resulting data outperformed training on the standard synthetic dataset. A second, outer meta-optimization loop (evolving the data-scientist agent's own harness/prompts/evaluation logic) raised validation pass rate from 12.8% to 42.4%.

## Mentioned in
- [LLM-autotrain](../../OrbiLLM/LLMtrain/LLM-autotrain.md)
