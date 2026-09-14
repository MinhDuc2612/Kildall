# Heretic

An open-source Python tool (github.com/p-e-w/heretic) by developer p-e-w, "Fully automatic censorship removal for language models" — was GitHub Trending's #1 Repository of the Day, roughly 22.5k stars when researched (independent trackers put it near ~27.1k by Aug 4, 2026, gaining ~42 stars/day), with well over 4,000 community-published decensored models on Hugging Face. Applies abliteration automatically: usage is `pip install -U heretic-llm` then `heretic <model-name>`, no manual layer/direction selection needed — it uses a TPE-based (Optuna) optimizer to jointly minimize refusal rate and KL-divergence from the original model's output distribution. Only applies to open-weight models (Llama, Qwen, Gemma, Mistral, etc.), not closed hosted models like ChatGPT or Gemini.

## Mentioned in
- [Uncensored Content](../../OrbiLLM/uncencored%20content.md)
