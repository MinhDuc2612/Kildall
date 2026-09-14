# groqccapi — Groq

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers used in every `ccapi` provider file**
> `✓P` primary source (provider docs or the repo README itself, read this session) ·
> `✓W` recovered from the deep-research workflow's fetch stage, source-attributed but **the
> adversarial verification stage failed** (all 25 verifier panels died on a session limit) ·
> `⚠` inferred or single-source. **No figure below was tested against a live API key.**

**One line:** the **fastest** free inference available (custom LPU hardware), and the clearest
documented case of a free tier whose published limits **decayed within two months**.

## ⚡ ANSWER FIRST — Groq

| | |
|---|---|
| **Free tier** | ✅ free, no card |
| **Limits** | measured **14,400 req/day, 6,000 TPM** |

**Verdict:** **Fastest free inference anywhere** (custom LPU chips). ⚠️ Size against **6,000 tokens/minute**, not the request count. And its limits *"rotted in under two months"*.

---

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [console.groq.com/keys](https://console.groq.com/keys) | ✓P |
| Base URL | `https://api.groq.com/openai/v1` | ✓P |
| Credit card | **Not required** | ✓P |
| Hardware | **LPU** — ultra-fast, Groq's own silicon | ✓P |
| Class | Inference provider (hosts others' models) | ✓P |

## Rate limits — and the decay warning

**Measured, May 2026 snapshot:** **14,400 requests/day** and **6,000 TPM** on
`llama-3.1-8b-instant`. `✓W`

> *"The exact ceiling rotted in under two months."* `✓W`

**That sentence is the most useful thing in this file** and applies to every provider here. It is
direct evidence against trusting any static catalogue — including `mnfst`, and including this file.

**The binding constraint is TPM, not RPD.** `✓W` Groq's measured **~6,000 TPM is the lowest of the
three measured** (Cerebras ~30,000, Mistral ~50,000). At 6,000 TPM a single 5,000-token prompt very
nearly exhausts your minute — **14,400 requests/day is unreachable in practice.** The generous-looking
RPD is theatre; the TPM is the real ceiling.

A separate catalogue lists **Moonshot Kimi K2 on Groq's free tier at 30 RPM / 250 RPD**, cited
without a link to Groq's own docs. `✓W` ⚠️ unsourced.

## Verdict

**Best free tier for latency-sensitive work**, and nothing else on this list is close on speed. But
size your workload against **~6,000 TPM**, not against the request count, and re-check limits monthly
— this is the provider with documented evidence of silent quota change.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — base URL, LPU note
2. Workflow run `wf_5cf67b3e-3b8` — measured 14,400 RPD / 6,000 TPM, the two-month decay observation, TPM-is-binding finding

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Groq**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
