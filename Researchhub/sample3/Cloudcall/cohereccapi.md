# cohereccapi — Cohere

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers used in every `ccapi` provider file**
> `✓P` primary source (provider docs or the repo README itself, read this session) ·
> `✓W` recovered from the deep-research workflow's fetch stage, source-attributed but **the
> adversarial verification stage failed** (all 25 verifier panels died on a session limit) ·
> `⚠` inferred or single-source. **No figure below was tested against a live API key.**

**One line:** the largest models on the free list (**Command A+ at 218B**, 256K context) — behind the
hardest restriction: **1,000 calls a month, non-commercial only.**

## ⚡ ANSWER FIRST — Cohere

| | |
|---|---|
| **Free tier** | ✅ free trial key, no card |
| **Limits** | ⚠️ **1,000 calls/month total** |

**Verdict:** **Evaluate, don't build.** ❌ **Non-commercial only** — the only provider here with a hard commercial ban. But Command A+ at 218B is the largest model on any free tier.

---

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [dashboard.cohere.com/api-keys](https://dashboard.cohere.com/api-keys) | ✓P |
| Base URL | `https://api.cohere.com/v2` | ✓P |
| Credit card | **Not required** | ✓P |
| Quota | **1,000 API calls/month total**, **20 RPM** ceiling | ✓P ✓W |
| Commercial use | ❌ **Prohibited — trial key is non-commercial only** | ✓P ✓W |
| Class | Provider API | ✓P |

## ⚠️ The restriction that disqualifies it for most uses

> *"1,000 calls per month total ... 20 requests/min ceiling ... **Trial key is non-commercial
> only**."* `✓W`

**This is the only provider in the 18 with an explicit commercial-use ban**, and 1,000 calls/month is
~33/day. It is a *trial*, dressed as a free tier — and note `mnfst`'s stated inclusion rule is
permanence with *"trial credits and time-limited promos don't count."* Cohere sits right on that
line.

## Models — 11, all at 20 RPM

| Model | Context | Max out | Modality |
|---|---|---|---|
| **Command A+ (218B)** | 128K | **64K** | Text + Image |
| **Command A (111B)** | **256K** | 8K | Text |
| Command A Reasoning | **256K** | 32K | Text (reasoning) |
| Command A Vision | 128K | 8K | Text + Image |
| Command A Translate | 8K | 8K | Text |
| Command R+ / R / R7B | 128K | 4K | Text |
| Command R7B Arabic | 128K | ~4K | Text |
| Aya Expanse 32B | 128K | 4K | Text |
| Aya Vision 32B | 16K | 4K | Text + Image |

`✓P` — read from the repo README. **218B is the largest model on any free tier in this set.**

## Verdict

**Use it to evaluate Command A+, not to build on.** 1,000 calls/month is an evaluation budget, and
the non-commercial term makes anything shipped a licence breach. Genuinely excellent for testing a
frontier-class 218B model and for Arabic and translation work, where its dedicated models have no
equivalent elsewhere on this list.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — full model table, quota, non-commercial flag
2. Workflow run `wf_5cf67b3e-3b8` — quota and restriction corroborated

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Cohere**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
