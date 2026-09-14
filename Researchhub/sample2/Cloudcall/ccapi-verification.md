# ccapi-verification — Did they actually work? Live probe, 2026-09-01

**What was asked:** check each provider one by one to see if it truly works.
**What was possible:** everything except sending a real inference request — **no API keys are held**,
so entitlement (does *your* free tier serve tokens) could not be tested. **Liveness, endpoint
correctness, and model rosters could**, and were.

**Method.** Unauthenticated `GET` to each documented signup page and each documented API base URL.
Read-only, no writes, no credentials. Interpretation:

| Code | Means |
|---|---|
| `200` | endpoint live **and** publishing its catalogue openly → **live model data recovered** |
| `401` / `403` | endpoint live, auth required → **URL is correct** |
| `000` / `404` | dead, or the documented path is wrong |

---

## Result 1 — every URL is live. 28 of 28.

**Repos (3/3):** `mnfst/awesome-free-llm-apis` `200` · `tashfeenahmed/freellmapi` `200` ·
`public-apis/public-apis` `200`

**Signup / key pages (16/16 reachable):** Aion Labs `200` · Cohere `200` · Gemini `200` ·
Mistral `307`→ · Z AI `200` · Cloudflare `403`* · Groq `200` · Hugging Face `200` · Kilo Code `200` ·
LLM7 `200` · ModelScope `200` · NVIDIA NIM `200` · Ollama `200` · OpenRouter `200` · OVHcloud `200` ·
SiliconFlow `200`

\* Cloudflare's `403` is its bot protection on the dashboard, not a dead link. Mistral's `307` is a
login redirect. Both are live.

**API base URLs (12/12 live):**

| Provider | Endpoint | Code | Meaning |
|---|---|---|---|
| Aion Labs | `api.aionlabs.ai/v1/models` | **200** | open catalogue |
| Hugging Face | `router.huggingface.co/v1/models` | **200** | open catalogue |
| Kilo Code | `api.kilo.ai/api/gateway/v1/models` | **200** | open catalogue |
| NVIDIA NIM | `integrate.api.nvidia.com/v1/models` | **200** | open catalogue |
| Ollama Cloud | `ollama.com/v1/models` | **200** | open catalogue |
| OpenRouter | `openrouter.ai/api/v1/models` | **200** | open catalogue |
| Cohere | `api.cohere.com/v2/models` | 401 | live — *"no api key supplied"* |
| Mistral | `api.mistral.ai/v1/models` | 401 | live — *"Invalid API Key"* |
| Groq | `api.groq.com/openai/v1/models` | 401 | live — *"Invalid API Key"* |
| Z AI | `open.bigmodel.cn/api/paas/v4/models` | 401 | live — auth header missing (message in Chinese) |
| Gemini | `generativelanguage.googleapis.com/v1beta/models` | 403 | live — *"Method doesn't allow unregistered callers"* |
| Cerebras | `api.cerebras.ai/v1/models` | 403 | live — *"Not authenticated"* |

**No dead endpoints. No wrong paths. Every base URL documented in the `ccapi` files is correct.**

---

## Result 2 — six catalogues answered openly, and that broke four claims

The `200` responses returned real model lists. Checking documented claims against them:

| # | Claim | Live result | Verdict |
|---|---|---|---|
| 1 | Aion Labs has **4** models, ids as listed | **exactly 4, ids match** | ✅ **exact** |
| 2 | Kilo Code has a **`kilo-auto/free`** model | **present**, plus 4 sibling auto tiers | ✅ **confirmed** |
| 3 | OpenRouter free pool is **"17+"** | **18 `:free` of 418 total** | ✅ count OK — ❌ **contents wrong** |
| 4 | Ollama Cloud has **16** model families | **19** | ❌ **understated** |
| 5 | NVIDIA NIM has **"100+"** models | **82** | ❌ **overstated ~20%** |
| 6 | Hugging Face is undocumented / unassessable | **134 models live** | ⚠️ **endpoint fine, terms still undocumented** |
| 7 | A rival catalogue lists **"Aion 2.5"** | **no such model exists** | ❌ **disproven** |

### 2a. OpenRouter's documented model table is materially stale

**Gone:** `openai/gpt-oss-20b:free`, `nvidia/nemotron-nano-9b-v2:free`,
`nvidia/nemotron-nano-12b-v2-vl:free`. **Renamed:** `nemotron-3-nano-30b-a3b` →
`nemotron-3-nano-omni-30b-a3b-reasoning`, `ling-3.0-flash` → `ling-3.0-flash-fin`.

**And the repo misses the best of it.** Live and undocumented:

- **`nvidia/nemotron-3-ultra-550b-a55b:free`** — a **550B** model, free, **1M context**
- **`z-ai/glm-5.2:free`** — GLM-5.2, the model `../OrbiOSS.md` rates top open-weights for maths/reasoning
- `minimax/minimax-m3:free`, `thinkingmachines/inkling:free`, `inkling-small:free`,
  `nvidia/nemotron-3.5-lightning:free` — **all 1M context**
- `dots-studio/dots-3-note-preview:free` (512K), `minimax/minimax-m2.7:free`,
  `nvidia/nemotron-3.5-content-safety:free`, `liquid/lfm-2.5-2.6b:free`

**Six free models now carry 1M-token windows.** OpenRouter's free tier is considerably better than
any catalogue in this research describes.

### 2b. Kilo Code being a proxy is now proven, not inferred

Kilo's catalogue **contains OpenRouter's own router products** — `openrouter/auto` and
`openrouter/free` — **and OpenRouter's `:free` model ids byte-for-byte**. Kilo is reselling
OpenRouter's free pool under its own gateway.

**Privacy consequence:** a request can traverse **Kilo → OpenRouter → the real upstream**, and the
logging policy that binds you is the last hop's — which you cannot see. It is a *superset*, though:
`stepfun/step-3.7-flash:free` and `meituan/longcat-2.0-free` appear on Kilo and not on OpenRouter.

### 2c. Ollama Cloud's roster is stronger than documented

19 live families, including `kimi-k3`, `glm-5.3`, `glm-5.2`, `deepseek-v4-pro:0813`,
`qwen3.5:397b`, `mistral-large-3:675b`, `nemotron-3-ultra`. **These are precisely the models
`../OrbiOSS.md` identifies as leading open weights**, and the same names run locally — the
local-fallback argument, confirmed.

---

## What this did NOT verify

**The most important things still rest on unverified claims.** Be clear about the line:

| Verified by probe ✅ | Still unverified ❌ |
|---|---|
| Endpoint exists and responds | Whether a free key is actually granted |
| Base URL is correct | Actual rate limits (RPM / RPD / TPM) |
| Model roster and ids | Whether those models are free *to you* |
| Context windows (where published) | Data-training policy |
| OpenAI-compatible shape | Commercial-use terms |
| Signup page reachable | Card / identity requirements |

**A `200` on `/v1/models` proves the shop is open. It does not prove anything is free.** Every
rate limit, quota and data-policy statement in the `ccapi` files remains `✓W`-tier — recovered from a
research run whose adversarial verification stage failed — or `✓P` from a repo README.

**Providers with no catalogue endpoint to check:** LLM7.io, OVHcloud, SiliconFlow, ModelScope,
OpenCode Zen, Cloudflare — no documented base URL was available to probe, so only their signup pages
were confirmed reachable.

**To close the remaining gap:** obtain a free key for the two or three providers that matter to you
and send one real request. That is the only test that settles entitlement, and it takes minutes.

---

## Files corrected as a result

`openrouterccapi.md` · `ollamacloudccapi.md` · `nvidianimccapi.md` · `huggingfaceccapi.md` ·
`kilocodeccapi.md` · `aionlabsccapi.md` — each now carries a **LIVE VERIFICATION** section with the
probe date and what changed.

## Sources

All evidence in this file is **first-party**: unauthenticated HTTP probes issued directly to each
provider's own signup page and API endpoint on 2026-09-01, plus live GitHub API metadata for the three
repositories. No secondary source was used, because the entire point of the exercise was to stop
relying on them. Endpoint list and per-provider detail: the 21 `ccapi` files.

## Change Log

- **2026-09-01** — Ran an unauthenticated liveness probe across all 21 `ccapi` files' endpoints in
  response to "check each of them one by one to see if it truly works." **Result: 28 of 28 URLs live,
  zero dead endpoints, every documented base URL correct** — 6 returning open catalogues (`200`), 6
  correctly refusing auth (`401`/`403`).
  Using the six open catalogues, checked documented claims against live data and found **four
  errors**: OpenRouter's model table is materially stale (3 models gone, 2 renamed, and **10 free
  models missing from the docs including a 550B model with a 1M window and a free GLM-5.2**); Ollama
  Cloud has **19** families, not the documented 16; NVIDIA NIM has **82** models, not "100+"; and a
  rival catalogue's **"Aion 2.5" does not exist** on the live endpoint, confirming the ⚠️ flag placed
  on it earlier. Two claims **confirmed exactly**: Aion Labs' 4 model ids match perfectly (the only
  provider in the set whose documentation matches its live endpoint exactly), and `kilo-auto/free`
  exists as documented.
  Upgraded one inference to proof: **Kilo Code's catalogue contains `openrouter/auto`,
  `openrouter/free` and OpenRouter's `:free` ids verbatim**, demonstrating it resells OpenRouter's
  free pool — so a request may traverse Kilo → OpenRouter → upstream with the last hop's logging
  policy binding.
  Stated the limit of this exercise plainly: **a `200` proves the endpoint is live, not that anything
  is free.** Rate limits, quotas, data policies, card requirements and commercial terms were **not**
  verified and still rest on repo READMEs or on a research run whose verification stage failed.
