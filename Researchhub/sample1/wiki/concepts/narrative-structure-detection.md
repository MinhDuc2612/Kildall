# Narrative-structure AI detection

StoryScope's core finding: the reliable tell separating AI-generated fiction from human fiction isn't style (word predictability/perplexity, sentence-length variance/burstiness, stock phrases) but narrative *shape* — who resolves the conflict, whether the ending is tidy, whether the theme is stated outright, whether time moves linearly. A classifier trained only on narrative-structure features (no style features) hits 93.2% macro-F1, retaining over 97% of a model that also gets style features (96.0%). Crucially, rewriting AI stories to scrub stylistic AI-tells (what a "humanizer" tool does) barely drops detection (95.5%→93.9%) — the structural signal survives surface-level editing, because it operates one level above sentence-level style.

## Mentioned in
- [Text Humanize](../../OrbiLLM/text%20humanize.md)
