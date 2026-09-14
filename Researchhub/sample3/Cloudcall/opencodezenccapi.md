# opencodezenccapi — OpenCode Zen

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** one of only **two providers `freellmapi` carries that `mnfst` deliberately does not** —
and that absence is the most informative fact available about it.

## ⚡ ANSWER FIRST — OpenCode Zen

| | |
|---|---|
| **Free tier** | unestablished |
| **Limits** | unestablished |
| **Data policy** | unestablished |

**Verdict:** ⚠️ **Least-supported file in this set.** Present in one aggregator, **absent from the permanence-filtered one**. Establish whether its access is permanent or trial credits before using it.

---

## Facts

| Field | Value | Tier |
|---|---|---|
| Listed in `freellmapi`? | ✅ Yes — in the 12-logo provider grid | ✓P |
| Listed in `mnfst`? | ❌ **No** | ✓P |
| Class | Inference provider, coding-focused | ⚠ |
| Base URL / limits / models / data policy | **none established** | — |

## Read the absence

`mnfst`'s inclusion criterion is explicit and strict:

> *"LLM APIs with **permanent** free tiers ... **Trial credits and time-limited promos don't
> count**."* `✓P`

**OpenCode Zen and Cerebras are the only two providers in `freellmapi`'s grid that `mnfst` omits.**
For Cerebras there is a documented reason — it silently cut its free catalogue from a dozen models to
two (`cerebrasccapi.md`). For OpenCode Zen, **no reason was established.**

Three readings, none confirmed:
1. Its free access is **trial credits**, which `mnfst` excludes by rule
2. It is **too new** to have been submitted to `mnfst`
3. It was simply **missed** — `mnfst` is PR-driven and 5 months old

**No evidence distinguishes these.** The absence is a signal to check, not a verdict.

## ⚠️ Honest gap — this is the least-supported file in the set

No provider documentation for OpenCode Zen was reached in this research. No base URL, no rate limits,
no model list, no data policy, no free-vs-trial determination. The name appears in `freellmapi`'s
provider grid and nowhere else in the sources read.

**Nothing is invented here.** OpenCode itself appears separately in `freellmapi`'s *compatible client*
list (alongside Claude Code, Aider, Cline, Cursor, Zed and others), which suggests a relationship
between the OpenCode coding agent and this endpoint — **but that connection was not verified.**

## Verdict

**Unassessed.** Present in one aggregator, absent from the one that filters for permanence. Before
using it, establish first whether its free access is permanent or trial credits — that single
question decides whether it belongs in this set at all.

## Sources
1. [`tashfeenahmed/freellmapi`](https://github.com/tashfeenahmed/freellmapi) — provider grid listing, compatible-client list
2. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — verified absence, and the stated permanence criterion

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **OpenCode Zen**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
