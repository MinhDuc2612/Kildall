# Text Humanize — Beating Narrative-Structure AI Detection

Source: Instagram reel (https://www.instagram.com/reel/DbvlXJBt7JB/), covering the "StoryScope" research paper. Instagram supplied no captions; audio was transcribed locally via whisper.cpp (`base.en` model) after the fact and cross-checked against the on-screen text read. Researched further via web search. Compiled 2026-08-19.

---

## 1. What the video is about

The reel walks through a real research paper: **StoryScope: Investigating idiosyncrasies in AI fiction** (Jenna Russell, Rishanth Rajendhran, Chau Minh Pham, Mohit Iyyer — University of Maryland; John Wieting — Google DeepMind). Preprint: arXiv 2604.03136. Code/data: github.com/jenna-russell/storyscope.

The core claim, as the video puts it: **the tell isn't word choice — it's shape.** Most AI-detection tools (GPTZero, Originality.ai, Turnitin's AI checker, etc.) look at *style*: word predictability (perplexity), sentence-length variance (burstiness), stock phrases, function-word ratios. Those are exactly the things "humanizer" tools try to fix by swapping synonyms and varying sentence length. StoryScope shows that's treating the symptom. The real signal lives one level up, in how the *story itself* is built: who resolves the conflict, whether the ending is tidy, whether the theme gets spelled out, whether time moves in a straight line.

## 2. What the research actually found

StoryScope built a pipeline that converts prose into a structured, style-free representation (grounded in **NarraBench**, a narratology taxonomy from Hamilton, Wilkens & Piper, 2025 — arXiv 2510.09869) across 10 dimensions: agents, social networks, events, plot, structure, setting, time, revelation, perspective, style. They ran this over 10,272 writing prompts, each answered by one human author and five LLMs (GPT, Claude, Gemini, DeepSeek, Kimi) — 61,608 stories total, ~5,000 words each — and mined 304 interpretable narrative features.

Headline results:
- A classifier trained **only** on narrative-structure features (no style features at all) hits **93.2% macro-F1** separating human from AI fiction — retaining over 97% of the score of a model that also gets style features (96.0%).
- A compact **30-feature core set** still reaches ~85% macro-F1.
- When they rewrote AI stories to scrub stylistic AI-tells (the exact move a "humanizer" tool makes), detection barely dropped — **95.5% → 93.9%**. Surface rewriting doesn't touch the structural signal.
- AI-generated stories cluster tightly together in narrative-feature space; human stories are far more spread out (per-story "rarity" score: human 0.71 vs AI 0.49). AI converges on one shape; humans don't.

The specific tells (human % vs AI %, from the paper's core-feature table):

| Narrative choice | Human | AI |
|---|---|---|
| Narrator states the theme/moral outright | 52% | 77% |
| Dialogue used to stage philosophical debate | 34% | 59% |
| Literary references are vague allusions, not named works | 50% | 72% |
| Story has no subplots at all | 57% | 79% |
| Ending resolved by the protagonist directly | 46% | 69% |
| Ending resolved via internal acceptance (vs. earned external change) | 27% | 47% |
| Emotion shown through physical sensation rather than named | 38% | 81% |
| Emotion named outright | 29% | 8% |
| Named texts/authors cited specifically | 47% | 24% |
| Fourth wall broken / direct reader address | 67% / 28% | 39% / 7% |
| Protagonist is morally ambivalent | 59% | 38% |

In short: **AI writes in a straight line.** One main character, one clean arc, the theme stated out loud, the ending closed and earned by the protagonist, references kept vague, time moving forward in order. Humans leave more loose ends, more ambiguity, more nonlinearity, and trust the reader to do inference work the AI insists on doing for them.

The narration adds three model-specific fingerprints beyond the core finding: Claude's stories rarely escalate tension (flat event trajectory), GPT leans on gossip as a plot device more than human writers do, and Gemini shows a bias toward dark, grim settings.

The video's middle section (multiple AI logos — GPT, Gemini, DeepSeek, Copilot, etc. — thrown at one identical prompt) makes the same point about AI tools generally, not just fiction: given the same brief, different models converge on a similar, generically "safe" solution shape, echoing the paper's finding that AI outputs cluster while human output doesn't.

## 3. Why the popular "humanize my AI text" tools mostly don't work against this

Broader research on AI-text detection backs up what the paper implies:
- **Paraphrase-based humanizers** (synonym swaps, sentence reshuffling) preserve the underlying generative structure — they don't touch discourse-level patterns like topic-sentence placement, resolution type, or thematic explicitness. They can nudge perplexity/burstiness scores but leave structural fingerprints intact.
- **Full cross-model rewrites** do better against perplexity/style detectors, but StoryScope's result shows structure-only detectors shrug off style-level edits almost entirely (that 95.5%→93.9% drop).
- **Logit watermarking** (e.g., green-list token schemes) is the one detection method current humanization approaches can't touch at all — but that's a provider-side signal, not something relevant to writing craft.

Conclusion: if the goal is text that reads as genuinely human — not just text that slips past a perplexity checker — the fix has to happen at the **structural/narrative-decision level**, before or alongside any sentence-level polishing.

## 4. The solution — a structural humanization protocol

This is not a word-swap checklist. It's a set of story-decisions to make deliberately, whether you're writing by hand, prompting an LLM, or editing AI output. Apply as many as fit the piece; even 3–4 of these meaningfully move a text out of the "AI cluster" StoryScope describes.

**A. Break the straight line (structure/time)**
- Don't tell events in strict chronological order. Add at least one flashback, a delayed reveal, or an in-media-res opening.
- Give the piece a subplot — even a small one — and don't fully resolve it. AI stories skip subplots 79% of the time; that absence is itself a tell.

**B. Don't close the loop cleanly (resolution)**
- Resolve the ending through something other than the protagonist single-handedly fixing the external problem. Let someone else help, let the problem partly persist, or resolve it through the protagonist's internal shift rather than decisive action.
- Leave one thread open. Real endings are earned, not administered — don't tie every bow.

**C. Trust the reader (theme)**
- Cut any sentence that states the "point" of the piece out loud. If a character or narrator explains the moral, delete it and let the preceding scene carry the weight instead.
- Keep literary/cultural references specific and named rather than vague ("like something out of a fable") — specificity reads human; vague gesturing reads AI.

**D. Make people morally mixed (agents)**
- Give the protagonist (or a key character) one choice that's compromised, selfish, or simply wrong — not villainous, just human. Purely sympathetic, cleanly-motivated protagonists are an AI tell.
- Show emotion through named feeling occasionally instead of always routing it through physical sensation ("her chest tightened") — the paper found AI over-indexes hard on somatic emotion cues (81% vs 38%).

**E. Layer in the surface fixes too (style — still matters for ensemble detectors)**
- Vary sentence length aggressively within paragraphs (mix sub-8-word sentences with 25+-word ones).
- Cut stock transitions and AI-vocabulary clusters (furthermore, moreover, it's worth noting, delve, seamlessly, paramount).
- Add one detail per section an LLM could not have invented — a real date, a specific number, a named place, a personal opinion.

**F. Process fix, not just prompt fix**
- If drafting with an LLM: have it produce the "bones" (structure, beats, research) and write the load-bearing sentences — theme, ending, key emotional beats — yourself. Voice tends to live exactly in the parts that get cut when people just accept the full AI draft.
- If instructing an LLM directly, bake these constraints into the prompt itself rather than fixing after the fact: explicitly ask for an unresolved subplot, a non-protagonist-driven resolution, no stated moral, nonlinear ordering, and morally mixed characters. Constraining generation beats post-hoc editing, since post-hoc editing tends to only reach the surface layer.

## 5. Sources

- StoryScope: Investigating idiosyncrasies in AI fiction — arXiv:2604.03136 (Russell, Rajendhran, Pham, Iyyer, Wieting; UMD + Google DeepMind) — https://arxiv.org/abs/2604.03136
- Code/data release — https://github.com/jenna-russell/storyscope
- NarraBench: A Comprehensive Framework for Narrative Benchmarking — Hamilton, Wilkens, Piper, 2025 — arXiv:2510.09869 — https://arxiv.org/html/2510.09869
- Coverage/summary: Tech Times, "AI Fiction Detection Reaches 93% on Structure Alone" (2026-07-05) — https://www.techtimes.com/articles/319753/20260705/ai-fiction-detection-reaches-93-structure-alone-style-edits-can-no-longer-fool-it.htm
- Coverage/summary: nowosci.ai — https://nowosci.ai/en/article/researchers-detect-ai-fiction-plot-structure
- Coverage/summary: AI Weekly — https://aiweekly.co/alerts/storyscope-detects-ai-fiction-by-narrative-shape-not-style
- General AI-detection mechanics (perplexity, burstiness, watermarking, why paraphrase-only humanizers fail) — multiple.chat detection/humanization writeup — https://multiple.chat/ai-detector-working-principles
- Bypass-resistance data across humanizer tools — https://aidetector.ac/how-it-works/
- Craft-level "sound human" technique roundups — writehybrid.com, eyesift.com, humangpt.io, wanderingeducators.com (2026 guides)

## 6. Change log
- 2026-08-19 — Created. Sourced from Instagram reel + deep research pass.
- 2026-08-19 — Redo pass: home-dir git mess cleared, local whisper.cpp transcript fully checked against this document line by line — no factual corrections needed, on-screen-text read from the first pass held up.
- 2026-08-20 — Link/claim verification sweep (part of a full Research docs sweep): every link and numeric claim re-checked against fresh sources, all confirmed accurate. No corrections needed. (Note: the paper is now on arXiv v6, accepted to COLM 2026 — worth knowing, not a correction.)
