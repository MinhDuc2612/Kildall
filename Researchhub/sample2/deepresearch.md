# deepresearch — HyperResearch, and what a deep-research harness should do

**Built:** 2026-09-02 · Sample 2 · self-contained
**Source watched:** [instagram.com/reel/DbfeuYpO-IF](https://www.instagram.com/reel/DbfeuYpO-IF/) —
**Ajay Yadav**, 2026-08-01, *"day 167 of building you 100x"*. Downloaded and transcribed locally with
`whisper.cpp` (no captions), 39 frames extracted.

**Why this file matters more than most in this folder:** the `/deep-research` workflow used repeatedly
in this very session **failed twice**, both times at its adversarial-verification stage, producing
zero verified claims. HyperResearch is a direct competitor to that design, and it addresses several of
the exact failure modes that broke it. Section 6 is the comparison.

---

## 1. Verified facts

Live GitHub API, 2026-09-02:

| Field | Value |
|---|---|
| Repo | [`jordan-gibbs/hyperresearch`](https://github.com/jordan-gibbs/hyperresearch) |
| Author | **Jordan Gibbs** |
| Licence | **MIT** |
| Stars / forks | **1,825 / 210** |
| Open issues | 26 |
| Language | Python |
| Created | 2026-04-09 |
| Last push | 2026-08-04 |
| Archived | No |
| Package | [`hyperresearch` on PyPI](https://pypi.org/project/hyperresearch/) |
| Requires | **Python 3.11–3.13** — 3.14 **not** supported |

**Install and use, verbatim from the README:**

```bash
cd your-project
pip install hyperresearch && hyperresearch install
```
Then `/hyperresearch <anything>` in Claude Code.

`hyperresearch install --global` makes it reachable from every session, at the stated cost of
*"~15 lines in every session's system reminder."* Per-project install keeps other sessions clean.

**Reel accuracy on the basics: good.** One-line install ✅, slash command ✅, uses the Claude Code
subscription you already pay for ✅, MIT open source ✅.

---

## 2. The architecture — a 16-step tier-adaptive pipeline

The reel compresses this to five bullets. The real design is more interesting, and one structural
decision stands out:

> *"The entry skill is a thin router... Each step's procedure loads into context **only when that step
> actually runs**. That's what stops a long pipeline from quietly dropping steps **as its context
> rots**."*

**That is the key engineering insight in the whole project.** A long research pipeline degrades not
because any step is wrong but because, by step 12, the instructions for step 12 are buried under
eleven steps of accumulated output. Loading each step's procedure **just in time** is a direct fix for
context rot — and it is the reason a 16-step pipeline is even attemptable.

**Tiering:** bounded queries auto-route to a **5-step fast path**; opt-in **dissertation** runs produce
**25K–80K words across chapters from 300–450 sources**, with a chapter-partition step (1.5) that
groups atomic items into 4–10 chapters and loops steps 2–10 per chapter.

---

## 3. The five design ideas worth stealing

Independent of whether the benchmark claim holds, these are good and most research harnesses lack them:

**1. Citation verification as a hard gate.**
> *"A skeptical cite-checker audits whether each cited source **actually supports its sentence**.
> Hallucinated quotes and unacknowledged retractions are **hard blocks** at the gate."*

Not "check the link resolves" — check the source **says the thing**. Unacknowledged retractions being
a blocking condition is unusually rigorous.

**2. Syndication does not count as consensus.**
> *"An independence audit clusters derivative copies, so **five reprints of one press release argue
> with the weight of one source**."*

This is the single most under-implemented idea in AI research tooling. Naive multi-source
"corroboration" mostly measures how widely one press release was reprinted. This file's own sibling
`OrbitoolOSS.md` hit exactly that failure — several sources agreeing because they were copying each other.

**3. The patcher physically cannot rewrite the report.**
> *"Four critics attack every draft in parallel, and a **tool-locked patcher can only apply surgical
> edits. It physically cannot rewrite the report.**"*

The reel's "four critics" is accurate. But the *constraint* is the clever half: without it, "fix the
criticism" degenerates into regenerating the document and losing everything that was already right.
**Capability restriction as a correctness mechanism.**

**4. Paywalled papers get read, not skimmed.**
> *"A closed paper normally enters a vault as a **1,500-character abstract that the report then cites
> as though it had been read**. Hyperresearch asks **Unpaywall and Europe PMC** for a legal
> open-access copy and stores the full text instead... Every substitution is disclosed."*

Naming the failure honestly — citing an abstract as though you read the paper — and disclosing every
substitution is exactly the standard this vault tries to hold.

**5. Crashed runs resume.**
> *"Each run keeps a manifest; `run resume` picks up at the exact step where it died."*

See section 6. This one is personal.

**And the compounding vault the reel emphasises:** every source lands in a **searchable
markdown + SQLite vault** that the next session reuses before fetching anything new. The reel's
*"your second report is smarter than your first"* is a fair rendering.

---

## 4. ⚠️ The benchmark claim — the repo is more honest than the reel

**What the reel says:** *"He ran it against the deep research benchmark, the one that scores AI reports
against PhD level work. It came out on top — above OpenAI's deep research, above Google's Gemini,
above NVIDIA's."*

**What the repository actually says**, in the caption directly under its own benchmark chart:

> *"**Forward-looking projection from a stratified pilot** against the DeepResearch-Bench leaderboard
> snapshot. **Third party validation is pending.**"*

And in the headline itself: *"currently leads the DeepResearch-Bench RACE leaderboard
**(benchmarked internally)**."*

**Three separate qualifiers the reel drops entirely:**

| Repo says | Meaning |
|---|---|
| *"forward-looking projection"* | **not a completed benchmark run** — an extrapolation |
| *"stratified pilot"* | a **sample**, not the full 100-query set |
| *"benchmarked internally"* + *"third party validation is pending"* | **self-reported, unvalidated** |

**The independent picture:** on DeepResearch Bench's own published evaluation, **Gemini-2.5-Pro Deep
Research leads overall at 48.88**, with OpenAI Deep Research following.

**And note who built the measuring stick.** The same author also publishes
[`jordan-gibbs/hyperresearchbench`](https://github.com/jordan-gibbs/hyperresearchbench) — *"DeepResearch-Bench
runner for Claude Code agents."* Publishing an agent-agnostic harness is a genuinely good contribution.
It also means **the tool, the benchmark runner, and the reported score all come from one party.**

**This is not an accusation of dishonesty — the repo states its own caveats plainly and the reel is
what removed them.** But the correct reading is *"a promising self-reported pilot result awaiting
third-party validation"*, not *"it beat OpenAI and Google."*

For completeness: the chart's own alt text names the compared systems as **Grep Deep Research, Cellcog
Max, nvidia-aiq, Gemini Deep Research and OpenAI Deep Research** — so the reel's "NVIDIA's" is
`nvidia-aiq`, and its list of competitors is accurate even where its conclusion is overstated.

---

## 5. DeepResearch Bench itself

| Field | Value |
|---|---|
| Repo | [`Ayanami0730/deep_research_bench`](https://github.com/Ayanami0730/deep_research_bench) |
| Site | [deepresearch-bench.github.io](https://deepresearch-bench.github.io/) |
| Leaderboard | [HF space: `muset-ai/DeepResearch-Bench-Leaderboard`](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard) |
| Size | **100 queries** |
| Metric named | **RACE** |

The reel's description — *"scores AI reports against PhD level work"* — is a loose but not unfair gloss
on a benchmark built to evaluate deep-research agents' report quality.

---

## 6. Against this session's `/deep-research` — a direct comparison

The `/deep-research` workflow was run twice in this session. **Both runs failed identically:** the
search and fetch stages completed, then **every one of the 25 adversarial verifier panels died** on an
account session-usage limit, returning **zero verified claims** both times. 91 of 103 agents errored on
run one; 91 of 105 on run two.

**How HyperResearch's design would have handled the same failures:**

| Failure hit this session | HyperResearch's stated answer |
|---|---|
| **Run died mid-way, all work lost** | *"Each run keeps a manifest; `run resume` picks up at the exact step where it died"* |
| **~100 agents fanned out at once, hit a rate limit** | tier-adaptive — bounded queries take a **5-step fast path** instead of the full 16 |
| **Verification all-or-nothing: 25 panels, all failed together** | verification is **distributed across steps** (cite-check gate, independence audit, four parallel critics) rather than one terminal stage |
| **Sources agreeing because they copy each other** | **independence audit** clusters derivative copies |
| **Claims recovered but unadjudicated** | **cite-checker is a hard block**, not an advisory pass |

**The structural lesson, stated plainly:** the workflow used here puts **all** verification in one
terminal stage, so when that stage fails the entire run yields nothing — which is exactly what happened,
twice. HyperResearch distributes verification across the pipeline and keeps a resume manifest. **On
architecture, it is the better design for this failure mode**, independent of any leaderboard claim.

**Worth trying** — it is MIT, one line to install, and runs on the Claude Code subscription already in
use. **Not yet worth believing on benchmarks.**

---

## 7. Honest gaps

- **HyperResearch was not installed or run.** Every capability above is quoted from its README. None
  was observed working.
- **Steps 3–16 were not read** — the README fetch captured the pipeline table through step 3
  (Contradiction gathering). The full step list is in the repo.
- **The benchmark chart image was not viewed**, only its alt text and caption. The actual plotted
  numbers are unverified.
- **DeepResearch Bench's leaderboard was not queried directly.** The Gemini-2.5-Pro 48.88 figure is
  from secondary coverage.
- **"250+ sources per run", "100–130 in the width sweep", "300–450 sources" for dissertation runs** —
  all author claims, none measured.
- **The reel's "$70/hour analyst" comparison** was not checked and is marketing framing, not a finding.
- **1,825 stars is modest** next to tools like `Socialpranker/deepdive` (376★) or `rohunvora/x-research-skill`
  (1,227★) in the same space — it is a real project with real adoption, not a dominant standard.

## 8. Sources

1. [`jordan-gibbs/hyperresearch`](https://github.com/jordan-gibbs/hyperresearch) — primary: README and live GitHub API metadata, 2026-09-02
2. [`hyperresearch` on PyPI](https://pypi.org/project/hyperresearch/)
3. [`jordan-gibbs/hyperresearchbench`](https://github.com/jordan-gibbs/hyperresearchbench) — the author's own DRB runner, MIT
4. [`Ayanami0730/deep_research_bench`](https://github.com/Ayanami0730/deep_research_bench) — the benchmark
5. [DeepResearch Bench site](https://deepresearch-bench.github.io/)
6. [DeepResearch-Bench Leaderboard (HF space)](https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard)
7. [I Built the Most Intelligent Deep Research Agent — Jordan Gibbs, Medium](https://medium.com/@jordan_gibbs/i-built-the-most-intelligent-deep-research-agent-13c3de5ebc8d)
8. [Converting Claude Code into the top scoring deep research agent — Hacker News](https://news.ycombinator.com/item?id=47953372)
9. Reel — [instagram.com/reel/DbfeuYpO-IF](https://www.instagram.com/reel/DbfeuYpO-IF/), Ajay Yadav, 2026-08-01

## Change Log

- **2026-09-02** — Created from one Instagram reel (Ajay Yadav, 2026-08-01), downloaded and
  **transcribed locally with `whisper.cpp`**. Subject identified and verified as
  **`jordan-gibbs/hyperresearch`** — **MIT, 1,825 stars, 210 forks, Python 3.11–3.13**, installed with
  `pip install hyperresearch && hyperresearch install` and invoked as `/hyperresearch` inside Claude Code.
  The reel's basic claims all check out: one-line install, slash command, MIT, runs on an existing
  Claude Code subscription, four parallel critics, persistent compounding source vault.
  Documented the architecture the reel compresses — a **16-step tier-adaptive pipeline** with a
  5-step fast path for bounded queries and dissertation runs of **25K–80K words from 300–450 sources**
  — and singled out its central engineering idea: **each step's procedure loads into context only when
  that step runs**, which the README frames as what *"stops a long pipeline from quietly dropping steps
  as its context rots."*
  Recorded five design ideas worth reusing: citation verification as a **hard gate** that checks whether
  a source actually supports its sentence (with unacknowledged retractions as blocking); an
  **independence audit** so *"five reprints of one press release argue with the weight of one source"*;
  a **tool-locked patcher that physically cannot rewrite the report**, only patch it; **Unpaywall and
  Europe PMC** substitution so paywalled papers are read in full rather than cited from a
  1,500-character abstract, with every substitution disclosed; and **resumable runs** via a per-run manifest.
  **Principal finding: the benchmark claim is far weaker than the reel presents, and the repository
  says so itself.** The reel says it *"came out on top above OpenAI's, above Google's, above NVIDIA's."*
  The repo's own chart caption reads *"**forward-looking projection from a stratified pilot**...
  **third party validation is pending**"*, and its headline qualifies the leaderboard claim as
  *"(benchmarked internally)."* Independently, **Gemini-2.5-Pro Deep Research leads DeepResearch Bench's
  published evaluation at 48.88.** Also noted that the same author publishes the benchmark *runner*
  (`hyperresearchbench`), so tool, harness and score share one origin — recorded as a
  self-benchmarking caveat, not an accusation, since **the repo states its caveats plainly and it is
  the reel that removed them**.
  Added a direct comparison against the `/deep-research` workflow used in this session, which **failed
  twice in exactly the same way** — search and fetch completing, then **all 25 adversarial verifier
  panels dying at once on a session-usage limit, yielding zero verified claims both times**.
  HyperResearch's **resume manifest**, **tier-adaptive routing**, and **verification distributed across
  steps rather than concentrated in one terminal stage** address precisely those failure modes.
  Conclusion recorded: **worth trying on architecture, not yet worth believing on benchmarks.**
