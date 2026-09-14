# mistralccapi — Mistral AI

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers used in every `ccapi` provider file**
> `✓P` primary source (provider docs or the repo README itself, read this session) ·
> `✓W` recovered from the deep-research workflow's fetch stage, source-attributed but **the
> adversarial verification stage failed** (all 25 verifier panels died on a session limit) ·
> `⚠` inferred or single-source. **No figure below was tested against a live API key.**

**One line:** free mode is **on by default**, gives **$10/month in credits** and **256K context on
almost everything** — and, like Google, has **stopped publishing its rate limits**.

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [console.mistral.ai/api-keys](https://console.mistral.ai/api-keys) | ✓P |
| Base URL | `https://api.mistral.ai/v1` | ✓P |
| Credit card | **Not required** | ✓P |
| Free allowance | **$10/month in API credits**, shared across Studio, API and Vibe Code | ✓W |
| Class | Provider API | ✓P |

## Rate limits — also unsourced

The repo lists **~1 RPS, 500K TPM**. Its own note says these are **stale carry-overs**:

> *"Mistral no longer publishes numeric free-tier rate limits and points you at the Limits page of
> the admin panel instead; the rate limit column is kept from the last published values."* `✓W`

**Independently measured TPM ceiling: ~50,000** — an order of magnitude below the listed 500K. `✓W`
That gap matters more than it looks, because **tokens-per-minute is the binding constraint on free
tiers in practice, not requests-per-day.** `✓W`

**Pool shape, measured:** Mistral is **one ~100M token/month pool shared across 13 models** — not
100M per model. `✓W` Any tool that multiplies per-model budgets is wrong by 13× here (see
`freellmapiccapi.md`).

## Models

All **256K context** except Codestral (128K):
Mistral Medium 3.5 (128B, text+image+code) · Mistral Small 4 · Mistral Large 3 (multimodal) ·
Ministral 3 in **3B / 8B / 14B** (text+vision) · **Codestral** (code, 128K). `✓P`

## Data policy — opt-out exists, and that is unusual

> *"Free-mode inputs and outputs may be used to train Mistral models, **and you can opt out at any
> time**."* `✓W`

**Mistral is the only provider in this set documented as offering a genuine training opt-out on the
free tier.** Google's carve-out is regional and automatic; Mistral's is a switch you control.

## Verdict

**The best-behaved free tier of the group.** European, opt-out available, no card, 256K context, a
real code model included. Ignore the 500K TPM figure — plan against the measured ~50K, and remember
the 100M/month is pooled across all 13 models.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — models, base URL, staleness note
2. Workflow run `wf_5cf67b3e-3b8` — measured ~50K TPM, 100M pooled quota, opt-out policy, $10 credits

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Mistral AI**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.
