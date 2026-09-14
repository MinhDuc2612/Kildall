# openrouterccapi — OpenRouter

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers** — `✓P` primary source read this session · `✓W` recovered from the deep-research
> workflow's fetch stage, source-attributed but **its verification stage failed** (all 25 verifier
> panels died on a session limit) · `⚠` inferred or single-source. **Nothing was tested with a live key.**

**One line:** the best-documented free pool here — **17+ models with explicit `:free` model ids at a
uniform 20 RPM / 50 RPD** — and a data policy that varies by whichever upstream you land on.

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [openrouter.ai/keys](https://openrouter.ai/keys) 🇺🇸 | ✓P |
| Base URL | `https://openrouter.ai/api/v1` | ✓P |
| Limits | **20 RPM, 50 RPD** — uniform across the free pool | ✓P |
| Class | Inference provider / router | ✓P |

## The free pool — models are explicitly tagged

OpenRouter's design choice is unusually clean: **free models carry a `:free` suffix in the model id**,
so free and paid can never be confused in code.

| Model | Context | Max out | Modality |
|---|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | **262K** | 262K | Text |
| `openai/gpt-oss-20b:free` | 131K | 32K | Text |
| `cohere/north-mini-code:free` | 256K | 64K | Text (code) |
| `google/gemma-4-31b-it:free` | 262K | 32K | Text + Image |
| `google/gemma-4-26b-a4b-it:free` | 262K | 32K | Text + Image |
| `inclusionai/ling-3.0-flash:free` | 262K | 32K | Text |
| `nvidia/nemotron-3-nano-30b-a3b:free` | 256K | — | Text |
| `nvidia/nemotron-nano-9b-v2:free` | 128K | — | Text |
| `nvidia/nemotron-nano-12b-v2-vl:free` | 128K | 128K | Text + Image |
| `poolside/laguna-s-2.1:free` | 262K | 32K | Text (code) |
| `poolside/laguna-xs-2.1:free` | 262K | 32K | Text (code) |
| *+ 6 more free models* | varies | varies | Text / Image |

All at **20 RPM / 50 RPD**. `✓P`

## The real constraint: 50 requests per day

**50 RPD is the tightest request budget on this list** — about one request every 29 minutes if spread
evenly. The 262K context windows are generous, but you get ~50 shots at them. **Good for occasional
big-context work, useless for an agent loop** (which can burn 50 calls in a single task).

## ⚠️ Data policy

> *"Free providers may log prompts for training."* `✓W`

Note the wording: **free *providers*, plural.** OpenRouter routes to upstreams, so the policy that
applies depends on which upstream served your request — the same opacity problem as Kilo Code
(`kilocodeccapi.md`), though OpenRouter at least lets you pin a specific model id.

## Verdict

**The best-engineered free tier here.** Explicit `:free` ids, uniform limits, a genuinely strong model
roster (a 120B Nemotron, Gemma 4, two poolside code models) and huge context windows. **Its 50 RPD
makes it a considered-use tier, not a workhorse** — and pin your model id if the data policy matters,
since "free providers may log prompts" is not something you can opt out of.


---

## ✅ LIVE VERIFICATION — 2026-09-01 · **the repo's model table is materially stale**

Probed `https://openrouter.ai/api/v1/models` unauthenticated (returns `200`, open catalogue).

**Live: 418 total models, 18 with a `:free` suffix.** The count roughly matches the repo's "17+".
**The contents do not.**

**Gone since the repo's snapshot — do not code against these:**

| Model in repo | Live status |
|---|---|
| `openai/gpt-oss-20b:free` | ❌ **absent** |
| `nvidia/nemotron-nano-9b-v2:free` | ❌ **absent** |
| `nvidia/nemotron-nano-12b-v2-vl:free` | ❌ **absent** |
| `nvidia/nemotron-3-nano-30b-a3b:free` | ❌ renamed → `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` |
| `inclusionai/ling-3.0-flash:free` | ❌ renamed → `inclusionai/ling-3.0-flash-fin:free` |

**Still live, exactly as documented:** `nvidia/nemotron-3-super-120b-a12b:free` (262K) ·
`cohere/north-mini-code:free` (256K) · `google/gemma-4-31b-it:free` · `google/gemma-4-26b-a4b-it:free`
(both 262K) · `poolside/laguna-s-2.1:free` · `poolside/laguna-xs-2.1:free` (both 262K).

**Live and MISSING from the repo — including the best models on the whole free tier:**

| Model | Context | Why it matters |
|---|---|---|
| **`nvidia/nemotron-3-ultra-550b-a55b:free`** | **1,000,000** | **A 550B model, free, with a 1M window** |
| **`z-ai/glm-5.2:free`** | 256,000 | **GLM-5.2 free** — the same model `../OrbiOSS.md` rates top open-weights for math/reasoning |
| `minimax/minimax-m3:free` | **1,048,576** | 1M context |
| `thinkingmachines/inkling:free` | **1,048,576** | 1M context |
| `thinkingmachines/inkling-small:free` | **1,048,576** | 1M context |
| `nvidia/nemotron-3.5-lightning:free` | **1,000,000** | 1M context |
| `dots-studio/dots-3-note-preview:free` | 512,000 | |
| `minimax/minimax-m2.7:free` | 196,608 | |
| `nvidia/nemotron-3.5-content-safety:free` | 128,000 | safety classifier |
| `liquid/lfm-2.5-2.6b:free` | 65,536 | small/fast |

**Verdict change: OpenRouter is far better than the repo suggests.** Six free models now carry
**1M-token context**, and a **550B** model is on the free tier. The 50 RPD limit still applies, but
what you get per request is dramatically larger than documented.

**Lesson:** the repo's table is a snapshot; **this endpoint is the source of truth and needs no key.**
Query it before choosing a model.

## Sources
1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — model table, limits, base URL
2. Workflow run `wf_5cf67b3e-3b8` — the free-provider logging policy

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **OpenRouter**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Live-verified 2026-09-01 against the provider's own `/v1/models` endpoint; see the **LIVE VERIFICATION** section above and `ccapi-verification.md`.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.
