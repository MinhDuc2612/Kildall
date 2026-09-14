# StoryScope

A research paper, "StoryScope: Investigating idiosyncrasies in AI fiction" (Jenna Russell, Rishanth Rajendhran, Chau Minh Pham, Mohit Iyyer — University of Maryland; John Wieting — Google DeepMind; arXiv:2604.03136, accepted to COLM 2026), built a pipeline that converts prose into a structured, style-free narrative representation (grounded in NarraBench) across 10 dimensions, run over 10,272 writing prompts each answered by one human author and five LLMs (GPT, Claude, Gemini, DeepSeek, Kimi) — 61,608 stories total. Core finding: a classifier trained only on narrative-structure features (no style features) hits 93.2% macro-F1 separating human from AI fiction, and rewriting AI stories to scrub stylistic tells barely moves detection (95.5%→93.9%) — the structural signal survives surface-level "humanizing."

## Mentioned in
- [Text Humanize](../../OrbiLLM/text%20humanize.md)
