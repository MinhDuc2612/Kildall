# modelscopeccapi — ModelScope

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** the **only provider here whose rate limits are sourced to its own published limits
page** — and one of the hardest to actually sign up for.

## ⚡ ANSWER FIRST — ModelScope

| | |
|---|---|
| **Free tier** | ✅ free for registered users |
| **Limits** | **2,000 req/day total, ≤500 per model** |

**Verdict:** **The only provider whose limits trace to its own published page.** ❌ But needs **Alibaba Cloud binding + real-name verification** — a hard blocker outside China.

---

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [modelscope.cn/my/myaccesstoken](https://modelscope.cn/my/myaccesstoken) 🇨🇳 | ✓P |
| Credit card | Not required | ✓P |
| **Identity** | ⚠️ **Alibaba Cloud account binding + real-name verification required** | ✓P |
| Class | Inference provider | ✓P |

## Rate limits — actually sourced, and dynamic

> *"API-Inference is free for registered users. Current published limits are **2,000 requests/day per
> user (total across models)**, with per-model daily quotas **dynamically adjusted and capped at
> 500**; concurrency is also dynamically rate-limited."* `✓W`

**This figure is attributed to ModelScope's own limits page** — making it, per the workflow's own
assessment, one of the few numbers in this whole set with a real primary source behind it.

Two structural notes:
1. **2,000 RPD is a total across all models**, not per model — the same pooled-quota shape found at
   Mistral and Cloudflare.
2. **Per-model caps are dynamic** (≤500/day) and **concurrency is dynamically limited.** So even the
   sourced number is a ceiling that moves. There is no stable contract here, only a published policy.

## ⚠️ The access barrier

**Alibaba Cloud account binding plus real-name verification.** Real-name verification in China
generally requires a Chinese national ID. **For most people outside China this is a hard blocker**,
regardless of the quota being generous.

If you want a Chinese provider without this, **Z AI accepts overseas phone numbers with no real-name
check** — see `zaiccapi.md`.

## Verdict

**Best-documented limits on the list, behind the highest access barrier on the list.** If you already
hold a verified Alibaba Cloud account, 2,000 requests/day is a solid free allowance with unusually
honest documentation. If you do not, this is not a realistic option.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — key page, verification requirement
2. Workflow run `wf_5cf67b3e-3b8` — the 2,000 RPD / ≤500 per-model figures, attributed to ModelScope's own limits page

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **ModelScope**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
