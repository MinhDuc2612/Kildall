# huggingfaceccapi — Hugging Face Inference

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** a router endpoint in front of the largest open-model hub in existence — and, in the
sources read for this file, **the thinnest documentation of any provider in the set.**

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) 🇺🇸 | ✓P |
| Base URL | **`https://router.huggingface.co/v1`** | ✓P |
| Class | Inference provider | ✓P |
| Free-tier terms | **not stated in the entry** | — |
| Rate limits | **not stated in the entry** | — |
| Credit card | **not stated in the entry** | — |

## ⚠️ Honest gap — most of this file is missing on purpose

`mnfst` lists Hugging Face with a base URL and nothing else: **no headline free-tier terms, no rate
limits, no card requirement.** The workflow's fetch stage did not return a Hugging Face-specific
source either.

**Rather than fill this in from memory, it is left blank.** Hugging Face's inference offering has
changed repeatedly (free serverless inference, then credits, then the router in front of third-party
providers), so a remembered figure would be worse than no figure.

**To complete this file:** read [huggingface.co/docs/inference-providers](https://huggingface.co/docs/inference-providers)
and the pricing page directly.

## What the base URL tells you

`router.huggingface.co` is a **router**, not a single inference backend. Like OpenRouter and Kilo
Code, it dispatches to third-party providers. That implies:
- the **data policy is the upstream's**, not necessarily Hugging Face's
- the **rate limit is the upstream's**
- **model availability is not guaranteed** — the same instability documented at Cerebras applies

Hugging Face is also named among the **11 providers whose free quota is a shared per-account pool**
that the `freellmapi` router over-counts. `✓W`

## Verdict

**Unassessable from the sources read.** The hub's reach is unmatched and the OpenAI-compatible router
is convenient, but no free-tier claim can responsibly be made here without reading Hugging Face's own
current docs. **This is the file in the set with the least behind it — treat it as a stub.**


## ⚡ ANSWER FIRST — Hugging Face

| | |
|---|---|
| **Free tier** | not documented in source |
| **Limits** | not documented |
| **Data policy** | not documented |

**Verdict:** **134 models live** on the router, including GLM-5.3 and Kimi-K3. ⚠️ **Terms unverified** — the endpoint is real and open, but no free-tier limits were ever published in the sources read.

---

---

## ✅ LIVE VERIFICATION — 2026-09-01 · **this is no longer a stub**

Probed `https://router.huggingface.co/v1/models` unauthenticated (`200`, open catalogue).

**Live count: 134 models.** The base URL documented above is **correct and serving**. The roster is
strong — the first entries alone include models `../OrbiOSS.md` rates at the top of the open-weight field:

`zai-org/GLM-5.3-Flash` · `zai-org/GLM-5.3` · `Qwen/Qwen3.8-27B` · `moonshotai/Kimi-K3` ·
`deepseek-ai/DeepSeek-V4-Flash-0731` · `ibm-granite/granite-4.2-30b` / `-8b` / `-3b`

**What this changes:** the "unassessable stub" verdict above was about *documentation*, and that part
stands — Hugging Face still publishes no free-tier terms in the source repo. But the **endpoint is
real, open, and carries 134 models including several frontier-class open weights.**

**Still unverified without a key:** free-tier quota, rate limits, card requirement, data policy.
Model *availability* is confirmed; model *entitlement* is not.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — base URL and listing only
2. Workflow run `wf_5cf67b3e-3b8` — Hugging Face named among pooled-quota providers

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Hugging Face**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Live-verified 2026-09-01 against the provider's own `/v1/models` endpoint; see the **LIVE VERIFICATION** section above and `ccapi-verification.md`.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
