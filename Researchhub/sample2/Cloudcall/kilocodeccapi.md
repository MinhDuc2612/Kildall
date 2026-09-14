# kilocodeccapi — Kilo Code

**Part of the `ccapi` set** · Built 2026-09-01 · Sample 2
Repo files: `mnfstccapi.md` · `freellmapiccapi.md` · `publicapisccapi.md`

> **Trust tiers used in every `ccapi` provider file**
> `✓P` primary source (provider docs or the repo README itself, read this session) ·
> `✓W` recovered from the deep-research workflow's fetch stage, source-attributed but **the
> adversarial verification stage failed** (all 25 verifier panels died on a session limit) ·
> `⚠` inferred or single-source. **No figure below was tested against a live API key.**

**One line:** **no API key and no credit card at all** — because Kilo is not an inference provider.
It is **itself an aggregating proxy** over other people's free tiers.

## Facts

| Field | Value | Tier |
|---|---|---|
| Key page | [app.kilo.ai/profile](https://app.kilo.ai/profile) | ✓P |
| Base URL | `https://api.kilo.ai/api/gateway` | ✓P |
| Credit card | **Not required** | ✓P |
| **API key** | **Not required either** | ✓P |
| Free model id | **`kilo-auto/free`** — auto-router over a free pool | ✓P |
| Class | Listed as an inference provider — **actually a router** | ✓W |

## The structural fact

> *"Kilo-provided model tier that automatically routes your requests to the best available free
> models."* `✓W`

Kilo's free tier is **"Auto Free"**, a routing layer that **forwards requests to third-party free
model providers rather than to Kilo-owned inference.** `✓W`

**So Kilo Code is doing exactly what `freellmapi` does** — aggregating other providers' free tiers
behind one endpoint — but hosted, and requiring no key at all. Whether that changes the
terms-of-service picture (see `freellmapiccapi.md`) is a question neither project fully resolves; the
difference is that with Kilo, *Kilo* holds the upstream relationship, not you.

**Kilo's own docs confirm it is free, not a trial:**
> *"Kilo Code can be used completely free of charge."* `✓W` — covering agentic coding conversations,
in-editor autocomplete and background tasks.

## Rate limits — there are none of its own

> *"Some free models may be rate limited by the upstream provider."* `✓W`

**Kilo publishes no RPM, no RPD, no token cap.** It explicitly defers to whatever upstream it routed
you to. **Any specific numeric limit you see attributed to Kilo Code's free tier has no primary
source.** `✓W`

## ⚠️ Data policy — the worst on this list

> *"Auto Free may route your requests to providers that log prompts and outputs and use them to
> improve their services. **Do not submit personal or confidential data**."* `✓W`

**No opt-out is offered.** The mitigation Kilo suggests is "don't send anything sensitive."

And because you cannot see which upstream you land on, **you cannot know whose policy applies to a
given request.** Concretely: when Auto Free routes through NVIDIA, NVIDIA's policy applies —
*"Your use is logged for security purposes and to improve NVIDIA products and services"* `✓W` — and
`mnfst` notes Kilo's NVIDIA-backed free endpoints are **trial-use-only with logging.** `✓W`

## Verdict

**The lowest-friction entry point on the entire list** — no card, no key, no signup, works inside
coding agents. And the **worst privacy position**: your prompt goes to an unknown upstream that may
train on it, with no opt-out and no visibility.

**Fine for**: throwaway coding help on public code.
**Not for**: anything private, proprietary, or under an NDA.


---

## ✅ LIVE VERIFICATION — 2026-09-01 · **`kilo-auto/free` confirmed, and the proxy claim is now proven**

Probed `https://api.kilo.ai/api/gateway/v1/models` unauthenticated (`200`, open catalogue).

**Live count: 363 models.** `kilo-auto/free` **exists exactly as documented.** ✅

**Five auto-routing tiers are live:** `kilo-auto/frontier` · `kilo-auto/balanced` ·
`kilo-auto/efficient` · **`kilo-auto/free`** · `kilo-auto/small`.

### The proxy claim is no longer an inference — the catalogue proves it

Kilo's own model list **contains OpenRouter's routers and OpenRouter's free models verbatim**:

- `openrouter/auto` and `openrouter/free` — **OpenRouter's own router products, listed as Kilo models**
- `poolside/laguna-s-2.1:free`, `poolside/laguna-xs-2.1:free`, `cohere/north-mini-code:free`,
  `minimax/minimax-m3:free`, `nvidia/nemotron-3-ultra-550b-a55b:free`, `thinkingmachines/inkling:free`,
  `dots-studio/dots-3-note-preview:free`, `liquid/lfm-2.5-2.6b:free`,
  `inclusionai/ling-3.0-flash-fin:free` — **the same `:free` ids OpenRouter serves, byte-for-byte**

**Kilo Code is reselling OpenRouter's free pool (among others) under its own gateway.** That is
direct, checkable evidence for the "aggregating proxy" claim, and it sharpens the privacy warning:
your prompt may traverse **Kilo → OpenRouter → the actual upstream**, and the logging policy that
applies is the last one's.

**Also live and exclusive to Kilo's list:** `stepfun/step-3.7-flash:free`,
`meituan/longcat-2.0-free` — free models not in OpenRouter's own catalogue, so the pool is a
superset, not a copy.

## Sources
1. [Kilo Code — using Kilo for free](https://kilo.ai/docs/getting-started/using-kilo-for-free) — primary docs, via workflow fetch stage
2. [`mnfst/awesome-free-llm-apis`](https://github.com/mnfst/awesome-free-llm-apis) — base URL, keyless note, NVIDIA trial-use flag

## Change Log

- **2026-09-01** — Created as part of the `ccapi` set covering **Kilo Code**, from the repo READMEs of
  `mnfst/awesome-free-llm-apis` and `tashfeenahmed/freellmapi` plus claims recovered from deep-research
  run `wf_5cf67b3e-3b8`, whose adversarial verification stage failed entirely (all 25 verifier panels
  died on a session limit) — so every `✓W` claim here is source-attributed but **unadjudicated**. Live-verified 2026-09-01 against the provider's own `/v1/models` endpoint; see the **LIVE VERIFICATION** section above and `ccapi-verification.md`.
- **2026-09-02 (re-sweep)** — Structural sweep of all 33 sample-2 files. This file's external links
  re-probed and reachable; no factual correction required.
