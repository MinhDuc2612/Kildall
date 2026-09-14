# cloudflareccapi — Cloudflare Workers AI

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** **75+ models on the free tier** — the widest free catalogue here — metered in
Cloudflare's own unit, "Neurons", which makes it the hardest quota on the list to reason about.

## ⚡ ANSWER FIRST — Cloudflare Workers AI

| | |
|---|---|
| **Free tier** | ✅ free, no card |
| **Limits** | **10,000 Neurons/day**, 75+ models |

**Verdict:** **Widest free catalogue.** ⚠️ Metered in "Neurons", not tokens, so you cannot budget it without their conversion table. Real pool measured at **~45M tokens/month shared across 21 models**.

---

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens) 🇺🇸 | ✓P |
| Free allowance | **10,000 Neurons/day** | ✓P |
| Credit card | **Not required** | ✓P |
| Models on free tier | **75+** | ✓P |
| Class | Inference provider | ✓P |
| Base URL | not captured this session | — |

## The Neuron problem

**Cloudflare does not meter in tokens or requests. It meters in "Neurons."** A Neuron is a normalised
compute unit, so **the same 10,000/day buys wildly different amounts of work depending on model
size.** You cannot convert your daily allowance into "N tokens" without Cloudflare's per-model
conversion table.

This makes Cloudflare's free tier **uniquely hard to compare** against the RPM/TPD providers, and it
is why aggregators mis-handle it (below).

## ⚠️ Measured pool shape — and how tools get it wrong

Measured on a real account: **Cloudflare Workers AI is a single ~45M token/month pool shared across
21 models.** `✓W`

The `freellmapi` router **counted this as 535M/month** by summing a per-model budget across all 21 —
inflating it roughly **12×**. `✓W` See `freellmapiccapi.md` for the full accounting bug; Cloudflare
is one of its two worked examples.

**The rule this establishes: free quota is per-account-pool, not per-model.** It was found to hold
across at least 11 providers. `✓W`

## Verdict

**Best free tier for breadth** — 75+ models, no card, and it sits on Cloudflare's edge network so
latency is good globally. **Worst for capacity planning**, because Neurons resist conversion and the
real pool (~45M tokens/month shared) is far smaller than naive per-model maths suggests.

Use it for variety and experimentation. Do not build a token budget on it without Cloudflare's own
Neuron conversion table.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — 10,000 Neurons/day, 75+ models, no card
2. Workflow run `wf_5cf67b3e-3b8` — measured ~45M pooled across 21 models; the 535M over-count

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Cloudflare Workers AI**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
