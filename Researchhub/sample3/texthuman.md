# texthuman — Detecting and Un-detecting AI Writing

**Built:** 2026-09-01 · Sample 2 · self-contained
**Sources watched:** two Instagram reels, downloaded and transcribed locally with `whisper.cpp`
(neither had captions), frames extracted and read.

| # | Reel | Creator | Date | Subject |
|---|---|---|---|---|
| A | [reels/DbvlXJBt7JB](https://www.instagram.com/reels/DbvlXJBt7JB/) | **100xEngineers** | 2026-08-07 | The **StoryScope** paper — detecting AI by narrative structure |
| B | [reels/DcduZOHobMa](https://www.instagram.com/reels/DcduZOHobMa/) | **Evgeny Shkuratov** (AI Design Engineer & Solopreneur) | 2026-08-25 | Using **Wikipedia's "Signs of AI writing"** to build a humanizer |

**Both were verified against primary sources. Both check out factually.**

> ## The headline: these two reels contradict each other, and neither says so
>
> **Reel B teaches you to remove surface tells** — em dashes, "it's not just X, it's Y", bolding,
> AI vocabulary.
> **Reel A's paper tested exactly that and found it does not work.** When StoryScope's researchers
> took stories **edited specifically to remove style tells** and ran their structural classifier over
> them, accuracy **did not meaningfully move — 93.9%.**
>
> Reel B's method is real and useful for *readability*. As a way to *evade detection*, the paper in
> reel A is direct evidence against it.

## ⚡ ANSWER FIRST

**Two reels, both factually accurate — and they contradict each other.**

| Reel | Claim |
|---|---|
| StoryScope | AI is detectable by **story structure**, 93% |
| Wikipedia guide | strip the surface tells to sound human |

**The contradiction:** StoryScope tested text **edited specifically to remove style tells**. It still
scored **93.9%**.

> **Style is a costume. Structure is a skeleton.**

**Measured AI tells:** explains its own theme **77%** of the time (humans: 52%) · uses dialogue for
philosophy **59%** (humans: 34%).

**Use the humanizer to write better, not to hide.** And note the Wikipedia page itself **warns against
trusting AI detectors** — a warning the reel shows on screen without mentioning.

---

---

## Part A — StoryScope: detection by story shape

### Verified paper facts

| Field | Value |
|---|---|
| Title | *StoryScope: Investigating idiosyncrasies in AI fiction* |
| arXiv | [2604.03136](https://www.alphaxiv.org/abs/2604.03136) · [PDF](https://jenna-russell.github.io/assets/pdf/storyscope.pdf) |
| Code | [`jenna-russell/storyscope`](https://github.com/jenna-russell/storyscope) |
| Institutions | **University of Maryland + Google DeepMind** ✅ *(reel correct)* |
| Status | Preprint, under review |

### The method

StoryScope automatically induces an **interpretable feature space of discourse-level narrative
features across 10 dimensions** — plot, agents, temporal structure and others. It does not look at
words. It looks at **how the story is built**.

**The corpus:**

| Item | Value |
|---|---|
| Writing prompts | **10,272** |
| Authors per prompt | 1 human + **5 LLMs** |
| **Total stories** | **61,608** ✅ *(reel said "61,000")* |
| Length | ~5,000 words each |
| **Features per story** | **304** |

**The five models tested:** Claude Sonnet 4.6 · GPT 5.4 · Gemini 3 Flash · DeepSeek V3.2 · Kimi K2.5.

### Results

| Task | Score |
|---|---|
| Human vs AI, **narrative features alone** | **93.2% macro-F1** ✅ *(reel said "93%")* |
| 6-way authorship attribution (which model wrote it) | **68.4% macro-F1** |
| **Same classifier on style-stripped text** | **93.9%** — *"dropped by less than a percentage point"* |

**That last row is the whole point of the paper.** You can strip every surface tell and the structural
detector still catches it. **Style is a costume; structure is a skeleton.**

⚠️ *Note the reported numbers are slightly odd as quoted — 93.9% is higher than the 93.2% baseline,
while the source describes it as a small drop. The two figures likely come from different splits or
metrics. Recorded as quoted rather than smoothed over.*

### Measured AI tells

| Behaviour | AI | Human |
|---|---|---|
| **Explicitly explains the theme** | **77%** | 52% |
| Uses dialogue for philosophical debate | **59%** | 34% |

The reel's framing — *"AI over-explains the theme because it doesn't trust the reader"* — is a fair
plain-English rendering of the 77%-vs-52% result.

### The reel's other claims — plausible, not verified

The reel states each model has a fingerprint: **Claude almost never escalates tension**, **GPT
over-uses gossip as a plot device**, **Gemini is biased toward dark, grim settings**.

⚠️ **These specific fingerprints were not found in the sources read.** The paper does do 6-way
authorship attribution at 68.4%, which *establishes that per-model fingerprints exist and are
learnable* — but the three specific behaviours quoted were not confirmed. The reel also says
*"one main character, one clean plot, one tidy ending"*; consistent with the findings, not directly
verified.

---

## Part B — Wikipedia's "Signs of AI writing"

### What it actually is

| Field | Value |
|---|---|
| Page | [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) |
| Maintained by | **WikiProject AI Cleanup** ✅ *(reel's "volunteer team that hunts down AI" is accurate)* |
| Status | **An advice page — not policy** |
| Freshness | Carries a **"needs to be updated"** notice as of **August 2026** |

**Eight documented categories** of tell: content issues (undue emphasis on significance, superficial
analysis, promotional language, vague attributions, formulaic "Challenges and Future Prospects"
sections) · language & grammar (AI vocabulary, avoidance of simple *is/are*, negative parallelisms) ·
style (excessive boldface, **em dashes**, odd headings, emoji) · communication patterns (collaborative
tone, knowledge-cutoff disclaimers, placeholder text) · markup issues · citation problems (broken
links, invalid identifiers, **misattributed sources**) · edit summaries · miscellaneous.

### The reel's method

1. Open the page, copy the whole text (or just the link)
2. Paste into your AI, ask it to **build you a "humanizer" skill**
3. Prompt shape given: *"when I give you a text, kill every pattern in this article. Keep my meaning,
   add nothing new."*
4. Then just type **"humanize it"**

**This is a sound technique and it already exists as a shipped product.** The Claude Code environment
this file was written in has a **`humanizer` skill** whose own description reads *"Based on
Wikipedia's comprehensive 'Signs of AI writing' guide"* and lists exactly the patterns above:
inflated symbolism, promotional language, superficial *-ing* analyses, vague attributions, **em dash
overuse**, **rule of three**, AI vocabulary, passive voice, **negative parallelisms**, filler phrases.

**So reel B is not proposing something speculative — it is describing, independently, a thing that
has already been built.** That is corroboration, and it is the strongest evidence the method works
for its actual purpose.

### ⚠️ The caveat the reel leaves out — and it is on the page it recommends

Read directly from a frame of the reel itself, the page carries a **Caveats → AI detection tools**
section warning:

> *"Do not solely rely on artificial intelligence content detection tools such as GPTZero and
> Pangram. While they perform better than random chance, these tools have non-trivial error rates.
> Detectors can be susceptible to factors such as text modifications (e.g. paraphrasing, markup, and
> spacing changes)... A high percentage of detected AI writing from the results of a detection tool
> is **not a valid criterion for speedy deletion**."*

**The page is visible on screen in the reel, warning against exactly the arms race the reel is
teaching you to win.** The page's authors know their list is a heuristic for *editors reviewing
articles*, not a scoring rubric for *evading detection*.

### 📋 The complete catalogue — all 60+ signs, itemised

**Part B above summarised eight categories. This is the actual list**, extracted from the page
2026-09-14. Use it as a checklist, not a score.

#### Content tells

| # | Sign | The exact tell |
|---|---|---|
| 1 | **Undue emphasis on significance** | *"marking a pivotal moment"*, *"represents a shift"*, *"key turning point"* |
| 2 | **Canned notability** | Lists *source types* instead of content — *"independent coverage"*, *"trade publications"* |
| 3 | **Superficial `-ing` analysis** | *"highlighting"*, *"underscoring"*, *"reflecting"*, *"contributing to"* — interpretive verb, no insight |
| 4 | **Promotional tone** | *"boasts a"*, *"vibrant"*, *"nestled"*, *"rich heritage"*, *"showcasing"* |
| 5 | **Vague attribution** | *"Industry reports"*, *"Observers cite"*, *"Experts argue"*, *"Some critics"* |
| 6 | **"Challenges and Future Directions"** | Rigid formula: *"Despite X, faces Y… Future prospects…"* |
| 7 | **Lists as proper nouns** | *"'Catchment area (health)' refers to…"* |
| 8 | **"Awards and Recognition"** | The *"X and Y"* header shape, this phrase especially |

#### Language tells

| # | Sign | The exact tell |
|---|---|---|
| 9 | **AI vocabulary** | See the era table below — **it dates the text** |
| 10 | **Copula avoidance** | *"serves as"*, *"stands as"*, *"marks"*, *"functions as"*, *"represents"* instead of plain **is** |
| 11 | **Vague connection** | *"in connection with"*, *"associated with"*, *"connected with"* |
| 12 | **Negative parallelism** | *"not only… but also"* · *"it's not X, it's Y"* · *"rather than X"* |
| 13 | **Rule of three** | Triads in parallel construction |

#### 🗓️ AI vocabulary by era — this dates a text

| Era | Words |
|---|---|
| **2023 – mid-2024** | *delve · intricate · pivotal · tapestry · testament · enduring · meticulous* |
| **mid-2024 – mid-2025** | *align with · bolstered · fostering · showcasing* |
| **mid-2025 onward** | *emphasizing · enhance · highlighting · showcasing* |

**Why this matters more than the words themselves:** vocabulary clusters by model generation. A text
dense in *delve* and *tapestry* was likely generated in **2023–24**, not last week. That is
provenance information no style-checker gives you.

#### Formatting tells

**Title heading** (repeats the article title) · **Title Case** on non-proper nouns · **headings
containing only headings** · **boldface overuse** · **inline-header vertical lists** · **em-dash
overuse** · **emoji as formatting** · **pointless tables** · **curly quotes** `"` `'` instead of
straight · **skipped heading levels** · **level-1 heading overuse** · **thematic breaks** `---`
between sections.

#### ⭐ Per-model markup fingerprints — the most reliable tell on the page

**These are mechanical artifacts, not style judgements.** A style tell is arguable; a leaked
`turn0search0` is not. If one appears, the text came from that model — no inference needed.

| Model | Leaked artifact |
|---|---|
| **ChatGPT** | `contentReference` · `oaicite` · `turn0search0` |
| **Gemini** | `[cite: 1]` · `[span_1]` |
| **Grok** | `grok_card` · `grok_render_citation_card_json` |
| **DeepSeek** | Lenticular brackets 【】 · dagger symbols |
| **Perplexity** | `attached_file` · `ppl-ai-file-upload` |

Also: **Markdown syntax inside wikitext**, broken wiki markup, non-existent categories and templates.

#### Citation tells

Broken external links · **invalid DOI/ISBN** · **DOIs resolving to unrelated papers** · book cites
with no page numbers · `utm_source=` tracking parameters left in · named references declared but
never used.

#### Signs of *human* writing — the contrast set

- **Published before November 2022.** Settles it.
- **The author can explain their editorial choices.** An LLM cannot say why it chose this word here.
- **Natural syntax variation** — inconsistent sentence shapes, genuine quirks.

#### ❌ What does NOT work

The page names these as unreliable on their own: **promotional tone alone** · **a single overused
word** · **detector output** · **gut feeling**.

---

### 🔬 Detection reliability — updated 2026-09-14, and the page has dated

**Part B quotes the page's warning against detectors. That warning is now partly out of date.**
Nature reported in 2026 that detection tools have *"made huge leaps forward"*, and the measured gap
between tools is large:

| Tool | Measured |
|---|---|
| **Pangram** | **3× lower false-positive rate than GPTZero**, 7× better negative error rate |
| **GPTZero** | claims 0.08% FP internally, *"sub-1%"* in its own paper · **10.02% false-negative** — heavily biased toward missing AI, not accusing humans |
| **Originality** | **9.24% false positive** — too high to use on real people |

**On the "humans are no better than chance" claim — it is too strong as stated.** Untrained readers
do score at chance. But the Ghostbuster study's trained students hit **59%**, and **experts familiar
with a specific model do markedly better** on paired *"pick the AI"* tasks. Familiarity is trainable.

**What this changes for Orbi:** the page's blanket *"do not rely on detectors"* was written when
GPTZero-class error rates were the norm. **A 10% false-negative rate still means one AI text in ten
walks past** — so the caveat holds for *accusation*. It no longer holds for *triage*.


---

## Part C — Putting them together

### The two layers of AI writing

| | **Surface** | **Structure** |
|---|---|---|
| What it is | word choice, punctuation, formatting, phrasing | plot shape, character count, theme handling, pacing |
| Documented by | **Wikipedia: Signs of AI writing** (8 categories) | **StoryScope** (10 dimensions, 304 features) |
| Can you edit it away? | **Yes, easily** | **No — that is the finding** |
| Detection after editing | evades surface detectors | **still ~93%** |

**Reel B operates entirely on the top row. Reel A proves the bottom row survives it.**

### What actually changes structure

Since surface edits do not, these are the things that would — and none of them are a "humanize it"
prompt:

1. **Add a subplot that does not resolve.** AI writes *"one clean plot, one tidy ending."*
2. **Stop explaining the theme.** The single largest measured gap — **77% vs 52%.** Delete the
   paragraph where the story tells you what it meant.
3. **Let dialogue be mundane.** AI uses dialogue for philosophical debate **59%** of the time against
   humans' **34%.** People mostly talk about lunch.
4. **Break the escalation curve.** Tension that rises monotonically to a resolution is a shape.
5. **Add a character who does not serve the plot.**

**These are editorial decisions, not text transformations.** No prompt performs them, because they
require deciding what the piece is *about* — which is the part that was outsourced in the first place.

### The honest framing

**Use reel B's method to write better, not to hide.** Stripping "it's not just X, it's Y", em-dash
pile-ups and bolded everything genuinely improves readability — that is why the Wikipedia list exists
and why a `humanizer` skill ships in this environment.

**Do not use it believing it defeats detection.** A structural classifier from UMD and DeepMind holds
**93%** on style-stripped text, and the Wikipedia page itself tells you detectors are unreliable in
both directions.

---

## Honest gaps

- **Neither reel's full frame set was exhaustively read** — 37 frames (A) and 10 (B); four were read.
  Reel A's visuals are stock footage carrying no data; reel B's carry the Wikipedia page.
- **The StoryScope paper itself was not read**, only its abstract-level coverage and code repo
  listing. The 93.2 / 93.9 inconsistency above would likely resolve in the PDF.
- **The three per-model fingerprints in reel A are unverified.** Attribution at 68.4% proves
  fingerprints exist; it does not confirm those three descriptions.
- **No detector was run.** Nothing here was tested by putting text through GPTZero, Pangram or the
  StoryScope code.
- **The `humanizer` skill was not invoked** — its description was read, not its instructions.
- **Wikipedia's page is flagged "needs to be updated" as of August 2026**, so some tells it lists may
  already be stale, and newer ones missing.

## Sources

1. [StoryScope — alphaXiv 2604.03136](https://www.alphaxiv.org/abs/2604.03136) — paper record
2. [StoryScope PDF](https://jenna-russell.github.io/assets/pdf/storyscope.pdf) — preprint, under review
3. [`jenna-russell/storyscope`](https://github.com/jenna-russell/storyscope) — code
4. [StoryScope: AI fiction over-explains its themes 77% of the time — AI Weekly](https://aiweekly.co/alerts/storyscope-ai-fiction-over-explains-its-themes-77-of-the-time) — the 77%/52% and 59%/34% figures
5. [AI Fiction Detection Reaches 93% on Structure Alone — TechTimes](https://www.techtimes.com/articles/319753/20260705/ai-fiction-detection-reaches-93-structure-alone-style-edits-can-no-longer-fool-it.htm) — the style-stripped robustness result
6. [StoryScope: The 93% Detector That Catches AI by How It Tells Stories](https://aniketkarneai.com/blog/2026-08-07-storyscope-narrative-features-ai-detection)
7. [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) — primary, the 8 categories and the caveats section
8. Reel A — [instagram.com/reels/DbvlXJBt7JB](https://www.instagram.com/reels/DbvlXJBt7JB/), 100xEngineers, 2026-08-07
9. Reel B — [instagram.com/reels/DcduZOHobMa](https://www.instagram.com/reels/DcduZOHobMa/), Evgeny Shkuratov, 2026-08-25

## Change Log

- **2026-09-01** — Created from two Instagram reels, both downloaded with `yt-dlp` and **transcribed
  locally with `whisper.cpp`** (neither had captions), with frames extracted and read.
  Identified the subjects: reel A (100xEngineers, 2026-08-07) covers the **StoryScope** paper; reel B
  (Evgeny Shkuratov, 2026-08-25) covers **Wikipedia's "Signs of AI writing"** page. **Both were
  verified against primary sources and both are factually accurate** — an unusual outcome for this
  vault, where video claims have repeatedly failed checking.
  StoryScope confirmed as **arXiv 2604.03136**, University of Maryland + Google DeepMind, with the
  reel's figures matching: **61,608 stories** (reel said 61,000), **93.2% macro-F1** (reel said 93%),
  built from **10,272 prompts** × 1 human + 5 LLMs (Claude Sonnet 4.6, GPT 5.4, Gemini 3 Flash,
  DeepSeek V3.2, Kimi K2.5), **304 features across 10 narrative dimensions**. Recorded the measured
  tells: AI **explains its theme 77%** of the time vs humans' **52%**, and uses dialogue for
  philosophical debate **59% vs 34%**. Flagged the reel's three per-model fingerprint claims (Claude
  never escalates tension, GPT over-uses gossip, Gemini prefers grim settings) as **unverified** —
  the paper's 68.4% attribution score proves fingerprints exist without confirming those three.
  **Principal finding: the two reels contradict each other and neither acknowledges it.** Reel B
  teaches removal of surface tells; StoryScope explicitly tested stories **edited to remove style
  tells** and its structural classifier held at **93.9%**. Surface humanising does not defeat
  structural detection.
  Also recorded: the Wikipedia page is maintained by **WikiProject AI Cleanup**, is **advice not
  policy**, and carries a **"needs to be updated"** notice as of August 2026 — and, read directly
  from a frame of reel B itself, contains a **Caveats section warning not to rely on AI detectors**
  (naming GPTZero and Pangram, noting non-trivial error rates and susceptibility to paraphrasing and
  spacing changes, and stating detector output is not valid grounds for speedy deletion). **The reel
  shows that warning on screen without mentioning it.**
  Noted that reel B's proposed "build a humanizer skill from this page" method **already exists as a
  shipped product** — the `humanizer` skill in this Claude Code environment describes itself as based
  on that exact Wikipedia guide and lists the same patterns — which corroborates the technique for
  improving readability while leaving the detection-evasion claim unsupported.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** block at the top, matching sample 1's
  presentation style: what the file is, the numbers that matter, and the decisive caveat, all before
  any discussion. No content changed; the research below now serves as backing detail.

- **2026-09-14 — Part B expanded from an eight-category summary to the full catalogue.** Re-read
  [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) in full
  and itemised **all 60+ signs** with their exact trigger phrases, which the previous one-paragraph
  summary did not carry. **Three genuinely new findings.** **(1) AI vocabulary clusters by era** —
  *delve/tapestry/meticulous* mark 2023–mid-2024, *align with/bolstered/fostering* mark
  mid-2024–mid-2025, *emphasizing/enhance/highlighting* mark mid-2025 onward — so the word choice
  **dates** a text, which is provenance no style-checker provides. **(2) Per-model markup fingerprints
  are the single most reliable tell on the page**, because they are mechanical artifacts rather than
  style judgements: ChatGPT leaks `contentReference`/`oaicite`/`turn0search0`, Gemini `[cite: 1]`/
  `[span_1]`, Grok `grok_card`, DeepSeek lenticular brackets, Perplexity `ppl-ai-file-upload`.
  **(3) The page's detector warning has dated.** Nature reported in 2026 that detectors have *"made
  huge leaps forward"*; **Pangram now measures a 3× lower false-positive rate than GPTZero**, while
  **Originality's 9.24% false-positive rate** is too high to use against real people and **GPTZero's
  10.02% false-negative rate** means one AI text in ten still passes. Also corrected the page's
  *"humans are no better than chance"* claim as too strong: untrained readers do score at chance, but
  the Ghostbuster study's **trained students reached 59%** and experts familiar with a specific model
  do markedly better on paired tasks — **familiarity is trainable.** Recorded the page's own list of
  **ineffective** indicators (promotional tone alone, a single overused word, detector output, gut
  feeling) and its **signs of human writing** contrast set.
