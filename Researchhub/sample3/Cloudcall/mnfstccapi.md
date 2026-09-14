# mnfstccapi — `mnfst/awesome-free-llm-apis`

**Repo:** [github.com/mnfst/awesome-free-llm-apis](https://github.com/mnfst/awesome-free-llm-apis)
**Built:** 2026-09-01 · Sample 2 · self-contained
**Part of the `ccapi` set** — see `freellmapiccapi.md`, `publicapisccapi.md`, and the 18 per-provider files.

**One line:** a curated, CC0-licensed list of LLM APIs with **permanent free tiers**, with per-model
rate limits and base URLs — the most *specific* of the three repos, and the only one that records
data-training policy per provider.

## ⚡ ANSWER FIRST — mnfst/awesome-free-llm-apis

| | |
|---|---|
| **Free tier** | **CC0-1.0** public domain |
| **Limits** | 7,255 stars, 16 providers |

**Verdict:** **The best of the three catalogues for choosing a provider.** ✅ Uniquely records **data-training policy** and **commercial restrictions** per provider. ⚠️ Vendor-maintained by Manifest.

---

---

## 1. Verified repository facts

Live GitHub API, 2026-09-01:

| Field | Value |
|---|---|
| Repo | `mnfst/awesome-free-llm-apis` |
| Description | *"List of Permanent Free LLM API (API Keys)"* |
| Licence | **CC0-1.0** — public domain, the most permissive possible |
| Stars / forks | **7,255 / 692** |
| Created | 2026-03-21 |
| Last push | 2026-08-21 |
| Archived | No |

**Structure:** `Provider APIs` (companies that train their own models) → `Inference providers`
(companies that host others' models) → `Glossary` → `Contributing`. That split is genuinely useful
and neither of the other two repos makes it.

**Commercial context, stated plainly:** the README carries a Manifest logo and the line *"All of
those free LLM APIs are available at manifest.build - make reliable agents."* The repo is
**maintained by a vendor whose product consumes these APIs.** That does not make the data wrong —
it is unusually detailed — but the list exists to feed a funnel. Worth knowing.

**Stated compatibility promise:** *"All endpoints are OpenAI SDK-compatible unless noted. Each link
points to the provider's API key page."*

---

## 2. The 16 providers

### Provider APIs — companies that train the models

| # | Provider | Country | Free-tier terms as listed | Base URL |
|---|---|---|---|---|
| 1 | **Aion Labs** | 🇮🇱 | Permanent free tier, **no credit card**. 15 RPM, 20K tokens/day. Roleplay/storytelling specialist | `https://api.aionlabs.ai/v1` |
| 2 | **Cohere** | 🇨🇦 | Free "Trial" key, no credit card. **1,000 API calls/month.** ⚠️ **Non-commercial use only** | `https://api.cohere.com/v2` |
| 3 | **Google Gemini** | 🇺🇸 | Free tier, no credit card. ⚠️ **"Free-tier prompts may be used by Google to improve products"** | `https://generativelanguage.googleapis.com/v1beta` |
| 4 | **Mistral AI** | 🇫🇷 | Free mode **on by default**, no credit card. **$10/month in credits.** ⚠️ **prompts may train Mistral models unless you opt out** | `https://api.mistral.ai/v1` |
| 5 | **Z AI (Zhipu)** | 🇨🇳 | Permanent free models, no credit card | `https://open.bigmodel.cn/api/paas/v4` |

### Inference providers — companies that host others' models

| # | Provider | Country | Free-tier terms as listed | Base URL |
|---|---|---|---|---|
| 6 | **Cloudflare Workers AI** | 🇺🇸 | **10,000 Neurons/day** free, no credit card. **75+ models** on free tier | — |
| 7 | **Groq** | 🇺🇸 | Free tier, no credit card. **Ultra-fast LPU inference** | `https://api.groq.com/openai/v1` |
| 8 | **Hugging Face** | 🇺🇸 | — | `https://router.huggingface.co/v1` |
| 9 | **Kilo Code** | 🇺🇸 | **No credit card AND no API key required.** `kilo-auto/free` auto-routes within a free pool | `https://api.kilo.ai/api/gateway` |
| 10 | **LLM7.io** | 🇬🇧 | — | — |
| 11 | **ModelScope** | 🇨🇳 | Free API-Inference for registered users. ⚠️ **requires Alibaba Cloud account binding + real-name verification** | — |
| 12 | **NVIDIA NIM** | 🇺🇸 | Free with NVIDIA Developer Program membership. **100+ models**, rate-limited per model | `https://integrate.api.nvidia.com/v1` |
| 13 | **Ollama Cloud** | 🇺🇸 | Free tier with usage limits. **16 cloud model families.** OpenAI-compatible via `ollama.com/v1` | `https://ollama.com/api` |
| 14 | **OpenRouter** | 🇺🇸 | Free `:free` model pool at **20 RPM, 50 RPD** | `https://openrouter.ai/api/v1` |
| 15 | **OVHcloud AI Endpoints** | 🇫🇷 | — | — |
| 16 | **SiliconFlow** | 🇨🇳 | Permanently free models, no credit card. ⚠️ **identity verification required.** 100+ in catalogue, **most of them paid** | — |

---

## 3. What the per-model tables actually contain

Each provider gets a table of `Model Name · Context · Max Output · Modality · Rate Limit`. That
granularity is the repo's real value. Samples taken verbatim:

**Cohere** — 11 models, all **20 RPM**, including Command A+ (218B, 128K ctx, 64K out, text+image),
Command A (111B, **256K ctx**), Command A Reasoning (256K/32K), Command A Translate, Command A
Vision, Command R7B Arabic, Aya Expanse 32B, Aya Vision 32B.

**Google Gemini** — 10 models, all **1M context** for the Flash line: Gemini 3.7 / 3.6 / 3.5 Flash
(65K out, text+image+audio+video), Flash-Lite variants at **30 RPM / 1,500 RPD**, standard Flash at
**15 RPM / 1,500 RPD**, Gemini 2.5 Pro at only **5 RPM / 50 RPD**, plus Gemma 4 31B and Gemma 4
26B-A4B at 256K.

**Mistral** — 7 models at **~1 RPS, 500K TPM**, all **256K context** except Codestral (128K):
Mistral Medium 3.5 (128B), Small 4, Large 3, Ministral 3 in 3B/8B/14B.

**Aion Labs** — 4 models, uniformly **15 RPM / 20K TPD**: aion-2.0, aion-3.0, aion-3.0-mini (all
128K, reasoning) and aion-rp-llama-3.1-8b (32K).

**OpenRouter** — 17 free models, uniformly **20 RPM / 50 RPD**, listed with explicit `:free` suffixes:
`nvidia/nemotron-3-super-120b-a12b:free` (262K), `openai/gpt-oss-20b:free` (131K),
`cohere/north-mini-code:free` (256K), `google/gemma-4-31b-it:free` and `gemma-4-26b-a4b-it:free`
(262K, text+image), `inclusionai/ling-3.0-flash:free`, three more Nemotron variants,
`poolside/laguna-s-2.1:free` and `laguna-xs-2.1:free` (262K, code), plus *"+ 6 more free models"*.

---

## 4. What this repo does better than the other two

1. **It records the data-training policy.** Gemini *"may be used by Google to improve products"*;
   Mistral *"may be used to train Mistral models unless you opt out."* Neither `freellmapi` nor
   `public-apis` surfaces this, and for a free tier it is the actual price you pay.
2. **It records commercial-use restrictions.** Cohere's trial key is flagged **non-commercial only** —
   a hard blocker that a rate-limit table alone would hide.
3. **It records identity friction, not just cost.** ModelScope needs Alibaba Cloud binding plus
   real-name verification; SiliconFlow needs identity verification. "Free, no credit card" is not
   the same as "free, no hurdle."
4. **It separates model-trainers from model-hosts.** A structural distinction that changes what you
   should expect about model availability and longevity.
5. **CC0-1.0.** Public domain — you can copy the whole dataset into anything with no obligation.

---

## 5. Honest limitations

- **Vendor-maintained.** Manifest builds agent tooling that consumes these APIs. Read the list as
  accurate-but-motivated.
- **Rate limits are secondhand.** Every figure here is the repo's transcription of a provider page,
  not a provider page. Free tiers change without notice — the per-provider files in this set are the
  place to check.
- **Several rows are incomplete.** Hugging Face, LLM7.io, OVHcloud and Cloudflare have no base URL or
  no headline terms in the sections captured here.
- **Model version churn.** The list names Gemini 3.7/3.6/3.5, Gemma 4, Mistral Large 3, Command A+ —
  a fast-moving roster where any snapshot ages in weeks.
- **Last push 2026-08-21**, so this snapshot is ~11 days stale as of writing. Active, not fresh.
- **"OpenAI SDK-compatible unless noted"** is a blanket claim covering 16 providers. It was not
  tested here for any of them.

## Sources

1. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — README fetched via GitHub API, and repo metadata, both 2026-09-01
2. [manifest.build](https://manifest.build) — the maintaining vendor

## Change Log

- **2026-09-01** — Created from the repo's own README and live GitHub API metadata (**CC0-1.0**,
  7,255 stars, 692 forks, pushed 2026-08-21, not archived). Enumerated all **16 providers**, split as
  the repo does into **5 model-trainers** (Aion Labs, Cohere, Google Gemini, Mistral, Z AI) and **11
  inference hosts** (Cloudflare, Groq, Hugging Face, Kilo Code, LLM7.io, ModelScope, NVIDIA NIM,
  Ollama Cloud, OpenRouter, OVHcloud, SiliconFlow), with base URLs and headline free-tier terms
  transcribed verbatim. Recorded the three things this repo captures that the other two do not:
  **data-training policy** (Gemini and Mistral both use free-tier prompts, Mistral with opt-out),
  **commercial-use restriction** (Cohere trial is non-commercial only), and **identity friction**
  (ModelScope needs Alibaba Cloud binding plus real-name verification; SiliconFlow needs identity
  verification). Flagged that the repo is **vendor-maintained by Manifest**, whose product consumes
  these APIs — accurate but motivated — and that all rate limits are the repo's transcription rather
  than primary provider documentation.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** verdict block at the top: free-tier status,
  limits, data policy where known, and a one-line verdict, before any detail. No content changed.
