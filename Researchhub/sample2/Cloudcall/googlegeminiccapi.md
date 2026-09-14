# googlegeminiccapi — Google Gemini (AI Studio)

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers used in every `ccapi` provider file**
> `✓P` primary source (provider docs or the repo README itself, read this session) ·
> `✓W` recovered from the deep-research workflow's fetch stage, source-attributed but **the
> adversarial verification stage failed** (all 25 verifier panels died on a session limit) ·
> `⚠` inferred or single-source. **No figure below was tested against a live API key.**

**One line:** the most generous free tier on the list by context window — **1M tokens on every Flash
model** — and the one whose rate limits **nobody can actually source any more**.

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | ✓P |
| Base URL | `https://generativelanguage.googleapis.com/v1beta` | ✓P |
| Credit card | **Not required** | ✓P |
| Class | Provider API (trains its own models) | ✓P |

## ⚠️ The rate limits are unsourced — this is the headline finding

**Google has stopped publishing per-model free-tier rate limits.** The `mnfst` repo's own footnote
concedes it:

> *"Google no longer publishes per-model free-tier rate limits; check your quotas in AI Studio."* `✓W`

So the figures below — **15 RPM / 1,500 RPD** for Flash, **5 RPM / 50 RPD** for 2.5 Pro, **30 RPM**
for Flash-Lite — are **carried over from a version of Google's docs that no longer exists.** Every
catalogue repeating them, including `mnfst`, is repeating an unsourced number. `✓W`

**Worse, quota is allocated per model and can be zero.** One practitioner measured
*"gemini-pro and flash-lite came back quota-zero"* while other models remained usable inside the free
allowance. `✓W` **The only real answer is your own AI Studio quota page.**

## Models listed

| Model | Context | Max out | Modality | Listed limit |
|---|---|---|---|---|
| Gemini 3.7 Flash | **1M** | 65K | Text+Image+Audio+Video | — |
| Gemini 3.6 Flash | **1M** | 65K | " | 15 RPM, 1,500 RPD ⚠️ |
| Gemini 3.5 Flash | **1M** | 65K | " | 15 RPM, 1,500 RPD ⚠️ |
| Gemini 3.5 Flash-Lite | **1M** | 65K | " | 30 RPM, 1,500 RPD ⚠️ |
| Gemini 3.1 Flash-Lite | **1M** | 65K | " | 30 RPM, 1,500 RPD ⚠️ |
| Gemini 2.5 Flash | **1M** | 65K | " | 15 RPM, 1,500 RPD ⚠️ |
| Gemini 2.5 Flash-Lite | **1M** | 65K | " | 30 RPM, 1,500 RPD ⚠️ |
| Gemini 2.5 Pro | **1M** | 65K | " | 5 RPM, 50 RPD ⚠️ |
| Gemma 4 31B | 256K | 32K | Text | — |
| Gemma 4 26B A4B | 256K | 32K | Text | — |

`✓P` for the roster and context windows (read from the repo README); `⚠️` on every rate limit.

## Data policy — the actual price

> *"Free-tier prompts may be used by Google to improve products, **except for users in the EEA,
> Switzerland and the UK**."* `✓W`

That regional carve-out is the single most useful fact in this file. **If you are in the EEA,
Switzerland or the UK, the free tier does not train on your prompts. Everywhere else, it does.**

Commercial use: reported as permitted **within the free quota**. `✓W`

## Verdict

**Best free tier here for long-context work** — 1M tokens, native multimodal, no card. Treat the
published RPM/RPD as folklore and read your own AI Studio quota page. Do not send anything
confidential unless you are in the EEA/Switzerland/UK.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — roster, base URL, footnote conceding Google stopped publishing limits
2. Workflow run `wf_5cf67b3e-3b8` fetch stage — data policy, regional carve-out, quota-zero observation

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Google Gemini**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.
