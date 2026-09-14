# zaiccapi — Z AI (Zhipu AI / BigModel)

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** permanent free models from the lab behind GLM — and, unusually for a Chinese provider,
**no real-name verification required** for the chat API.

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [open.bigmodel.cn/usercenter/apikeys](https://open.bigmodel.cn/usercenter/apikeys) 🇨🇳 | ✓P |
| Base URL | `https://open.bigmodel.cn/api/paas/v4` | ✓P |
| Credit card | **Not required** | ✓P |
| Identity | ✅ **Accepts overseas phone numbers; no real-name verification for the chat API** | ✓W |
| Class | Provider API (trains GLM) | ✓P |

## The verification point matters

The other two Chinese providers in this set are gated:
- **ModelScope** — Alibaba Cloud account binding **plus** real-name verification `✓P`
- **SiliconFlow** — identity verification required `✓P`
- **Z AI** — **overseas phone number accepted, no real-name check for chat** `✓W`

For anyone outside China, **Z AI is the accessible route to GLM-family models.** That is a
practical difference, not a detail: real-name verification generally requires a Chinese national ID.

## Models

`mnfst` lists Z AI's permanent free models but the section captured this session did not include the
full table. **Not filled in here rather than guessed.** GLM-family models are the expectation given
Zhipu trains GLM — and the `../OrbiOSS.md` file in this folder documents GLM-5.2 (MIT, 753B) and
GLM-5.3 as open weights, which is a separate route to the same family with no quota at all.

## Verdict

**The most accessible Chinese provider on the list**, and the only one that does not demand identity
documents. Worth a key if you want GLM-family output without self-hosting. If you *can* self-host,
note that GLM-5.2's weights are MIT-licensed — see `../OrbiOSS.md`.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — base URL, permanent-free claim, no card
2. Workflow run `wf_5cf67b3e-3b8` — the overseas-phone / no-real-name finding

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Z AI (Zhipu)**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Endpoint/signup page confirmed reachable 2026-09-01 (`ccapi-verification.md`); no open catalogue endpoint was available, so the model roster and limits are unverified.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.
