# ollamacloudccapi — Ollama Cloud

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** the hosted arm of the local-first Ollama project — **16 cloud model families**, free
tier with usage limits, and the only provider here with a genuine local fallback story.

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [ollama.com/settings/keys](https://ollama.com/settings/keys) 🇺🇸 | ✓P |
| Base URL | `https://ollama.com/api` | ✓P |
| OpenAI-compatible URL | `https://ollama.com/v1` | ✓P |
| Free tier | **Yes, with usage limits** — figures not published in the entry | ✓P |
| Models | **16 cloud model families** from the Ollama library | ✓P |
| Class | Inference provider | ✓P |

## The thing that makes it different

**Ollama is primarily a local runtime.** Every other provider in this set is cloud-only; if the free
tier changes or dies, you have nothing. With Ollama, the same model names you call in the cloud
generally run **on your own machine** with no quota at all.

For the Mac mini M4 setup documented in `../UHWmini.md`, that matters: **Ollama Cloud can be the
overflow path for a local-first stack** rather than the primary one. Note also that Ollama **switched
its backend to MLX in March 2026**, taking decode from 58 → 112 tok/s on a Mac mini — see `../UHWmini.md`.

## Rate limits

`mnfst` says **"free tier with usage limits"** and does not give numbers. `✓P` **No figures are
invented here.** Check your account page.

## Pool shape warning

Ollama appears in the list of **11 providers whose free quota is a shared per-account pool**, which
the `freellmapi` router was found to over-count by summing per-model budgets. `✓W` So treat any
aggregate "Ollama free tokens/month" figure from a third-party tool as inflated.

## Verdict

**The strategically safest free tier on the list**, because it is the only one with a zero-quota
escape hatch on your own hardware. Weakest on documentation — no published limits at all. Best used
as the cloud half of a local-first setup, not as a standalone free-inference source.


## ⚡ ANSWER FIRST — Ollama Cloud

| | |
|---|---|
| **Free tier** | ✅ free tier |
| **Limits** | not published |

**Verdict:** **Strategically the safest.** ✅ The only one with a **zero-quota escape hatch** — the same models run locally. Live roster includes kimi-k3, glm-5.3, deepseek-v4-pro.

---

---

## ✅ LIVE VERIFICATION — 2026-09-01 · **19 models, not 16**

Probed `https://ollama.com/v1/models` unauthenticated (`200`, open catalogue).

**The repo says "16 cloud model families." Live count is 19.** The roster is stronger than the repo
implies — it includes several models `../OrbiOSS.md` rates at the top of the open-weight field:

`kimi-k3` · `glm-5.3` · `glm-5.3-flash` · `glm-5.2` · `glm-5.1` · `deepseek-v4-pro:0813` ·
`deepseek-v4-flash:0731` · `qwen3.5:397b` · `mistral-large-3:675b` · `kimi-k2.7-code` · `kimi-k2.6` ·
`nemotron-3-ultra` · `nemotron-3-super` · `nemotron-3-nano:30b` · `minimax-m3` · `minimax-m2.7` ·
`gemma4:31b` · `gpt-oss:120b` · `gpt-oss:20b`

**Notable:** `kimi-k3`, `deepseek-v4-pro`, `glm-5.3` and `qwen3.5:397b` are all present — the exact
models this vault's `../OrbiOSS.md` identifies as leading open weights. Ollama Cloud gives hosted access
to them, and the same names run locally, which is the local-fallback argument in full.

**Verdict unchanged, evidence strengthened.** Still no published rate limits — that part could not be
verified without a key.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — base URLs, 16 families, usage-limited free tier
2. Workflow run `wf_5cf67b3e-3b8` — Ollama named among the pooled-quota providers
3. Companion file `../UHWmini.md` — the Ollama→MLX backend switch and local-first context

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Ollama Cloud**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Live-verified 2026-09-01 against the provider's own `/v1/models` endpoint; see the **LIVE VERIFICATION** section above and `ccapi-verification.md`.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
