# 6 AI features "worth the money" — verified, and what Kildall does instead

**Source:** Dan Martell, Instagram reel [Dd1B4uIFEI7](https://www.instagram.com/p/Dd1B4uIFEI7/), 22 s, watched 2026-09-30.
**Method:** frames + local whisper.cpp transcript → `/deep-research` (106 agents, 24 sources, 23 claims
confirmed 3-0, 2 refuted) → Grok Bot and Kimi Agent Swarm checked by hand against xAI and Hugging Face,
because the research budget verified only 25 of 113 extracted claims and never reached those two.

---

## ⚡ Answer first

| # | Feature | Real? | Cheapest plan that has it | Kildall equivalent | Local today? |
|---|---|---|---|---|---|
| 1 | **Perplexity Model Council** | ✅ | Max **$200/mo** (web/iOS) · or Computer credits on any paid plan | router + council over lanes / free cloud tiers | ⚠️ pattern only |
| 2 | **Wispr Flow Command Mode** | ✅ | Pro **~$12–15/mo** | Phase 9.3 voice + a selected-text transform | ❌ not built |
| 3 | **Claude Code Ultrareview** | ✅ | Pro/Max: **3 free runs, then ~$5–25 each** | Phase 4.4 subagents + a verify-each-finding loop | ❌ not built |
| 4 | **xAI Grok Bot** | ✅ beta | included in **SuperGrok / Cursor Pro+**, usage billed separately | Kildall + Hermes channels + 4C computer mode | ⚠️ partly (Phases 3–4) |
| 5 | **ElevenLabs Voice Cloning** | ✅ | Instant **$6/mo** · Professional **$22/mo** | **mlx-audio** / **chatterbox-mlx** (MIT) | ✅ tools exist, fit unmeasured |
| 6 | **Kimi Agent Swarm** | ✅ | Kimi paid tiers ($19–199/mo) — swarm on higher tiers | **Kimi K2.6 open weights** (Lane C) + Kildall subagents | ⚠️ weights yes, swarm runtime no |

🔑 **Every feature is real, and five of six are paid wrappers around a pattern Kildall is already planning to own**:
multi-model voting, voice commands, verified multi-agent review, an always-on agent with its own computer,
and swarms. Only voice cloning needs a new model, and MIT tools for it already run on Apple Silicon.

⚠️ **The reel is a lead magnet.** It ends: *"comment AI business and I'll send it over"* (his "AI company OS").
It gives no prices, limits or evidence. Everything below comes from vendor docs and the research run.

---

## 1. Perplexity Model Council — ✅ confirmed (3-0)

- **What:** one query goes to **three frontier models in parallel** (by default one each from Anthropic, OpenAI
  and Google, for example Claude Opus 4.6, GPT 5.2, Gemini 3.0). A separate **synthesizer ("chair") model**
  merges them and **shows where they agree and differ**.
- **Launched:** **2026-02-05**, Max only, web only. iOS came later (app v26.16.0+). No Android or desktop mode.
- **Plans:** web/iOS needs **Max ($200/mo, $2,000/yr) or Enterprise Max**, with no per-query charge up to an
  unpublished cap. Free, Pro, Education Pro and Enterprise Pro do not get it.
  **Since late July 2026** (Jul 28 vs 29 is unresolved) it is also a **Perplexity Computer skill on every paid
  plan**, choosing **2–8 models** (OpenAI, Anthropic, Google, GLM, Kimi) and billed in credits (100 = $1).
- **Evidence limits:** Perplexity's pages returned 403; confirmed via search snippets and consistent coverage.
  How it works is vendor-described; no independent benchmark.
- **Local equivalent:** [`karpathy/llm-council`](https://github.com/karpathy/llm-council) — each model answers,
  then each ranks the others anonymously, then a chairman writes the answer. ⚠️ **No licence file** (GitHub API:
  `license: null`), no update since 2025-11-22, and it calls cloud models via OpenRouter by default.
  **Kildall should re-implement the pattern, not reuse the code.**
- **Kildall fit:** 24 GB holds one resident text model, so a *local* council runs its members **one after
  another** (slow). A practical council = Lane A + the free Cloudcall tiers, with a local chair. Candidate for
  **Phase 7** (quality) or the router's hard-question path.

## 2. Wispr Flow Command Mode — ✅ confirmed (3-0)

- **What:** hold a shortcut, **speak an instruction instead of dictation**, release, and Flow runs it.
  In practice it **edits or transforms selected or nearby text**, or starts a web search (phrases starting with
  "ask", "search", "hey"). **It does not trigger general OS or agent actions.**
- **Plan:** **paid only** — on Free the shortcut does nothing. Pro ≈ $15/mo, or $12/mo billed yearly
  (prices from third-party write-ups, not Wispr). Mac and Windows; iOS gets search phrases only;
  **trigger phrases English-only.**
- **Not found:** launch date, independent review, local equivalent.
- **Kildall fit:** this is **Phase 9.3 voice** (faster-whisper → Kildall) plus reading and replacing the
  selected text through the **accessibility tree (Phase 4C layer A)**. Kildall's version can also run real
  actions, in English and Vietnamese.

## 3. Claude Code Ultrareview — ✅ confirmed (3-0)

- **What:** research-preview command **`/code-review ultra`** (alias `/ultrareview`). It starts a **fleet of
  reviewer agents in a cloud sandbox on Anthropic's infrastructure**, and **every finding is independently
  reproduced and verified** before it is reported. About 5–10 min per review.
- **Pricing:** Pro and Max get **3 free runs, once per account**; Team and Enterprise get none. Then **~$5–25
  per review in usage credits**, separate from plan usage — hence "for token maxers".
  Needs a claude.ai login; with API-key, Bedrock, Vertex, Foundry or Zero Data Retention it falls back to a
  normal local review.
- **Evidence limits:** "independently verified" is Anthropic's description; no outside benchmark.
- **Kildall fit:** the pattern = **Phase 4.4 subagents** (parallel reviewers) + a **verify-before-report loop**
  (the same rule this project already uses for research: 2 of 3 votes to keep a claim). No local tool verified.

## 4. xAI Grok Bot — ✅ confirmed from xAI's own pages (checked by hand)

- **What:** *"your team of always-on agents. They have their own computer, work inside tools and apps like you
  do, and keep working 24/7."* Named Bots with jobs and memory on a **persistent cloud computer** (browser,
  filesystem, terminal — per xAI docs) that sign into your tools, including ones with **no clean API or MCP**.
- **Launched:** **2026-08-11, beta**, desktop + iOS ([xAI](https://x.ai/news/introducing-grok-bot)).
  **2026-08-26:** included in **all SuperGrok, Cursor Pro and Cursor Teams plans**
  ([xAI](https://x.ai/news/grok-bot-more-plans)); it *"comes with its own usage, separate from your Grok and
  Cursor plans."* Enterprise version and Team Bots followed.
- ⚠️ **Unverified, secondary sources only:** a "$200/mo standalone after a 14-day trial" price, and "no reach
  through email, Slack or Telegram". Limits reported by reviewers: cloud-only, xAI models only, no memory
  export, Bots on one account share one computer and its permissions.
- **Kildall fit:** this is the closest product to what Kildall is becoming — **but local**: Kildall's agent
  loop and permission executor (Phases 3–4), **computer mode (4C)**, **Hermes channels (9.2)**, and memory
  that **you can read and export**. The "shared permissions across Bots" weakness is exactly what Kildall's
  per-action permission executor avoids.

## 5. ElevenLabs Voice Cloning — ✅ confirmed (3-0)

- **Instant Voice Cloning:** under 2 min of audio (1–2 min recommended). From **Starter, $6/mo**; not on Free.
- **Professional Voice Cloning (PVC):** a fine-tuned voice. From **Creator, $22/mo** ($11 first month,
  121k credits). Slots: Creator/Pro/legacy Scale 1 · Scale/legacy Business 3 · Business 10 · Enterprise custom ·
  Free/Starter 0. Needs **≥ 30 min** of audio; **2–3 h** ideal. 🔴 **Your own voice only** (even with someone's
  consent), with a **spoken verification step**.
- **Refuted and dropped (0-3):** a claim that a Consumer Reports study named which cloning firms lack safeguards.
- **Local equivalents (verified 3-0):**
  - [`Blaizzy/mlx-audio`](https://github.com/Blaizzy/mlx-audio) — **MIT**, ~7,964★, pushed 2026-09-28. STT, TTS
    and speech-to-speech on MLX; **zero-shot cloning from a reference clip + its transcript** using OmniVoice,
    Qwen3-TTS, CSM, Higgs Audio v2/v3, VoxCPM2, MOSS-TTS.
  - [`chatterbox-mlx`](https://pypi.org/project/chatterbox-mlx/) — **MIT**, v1.0.6, MLX fork of Resemble AI's
    Chatterbox, clones via `--voice`. One maintainer; speed claims are the author's own.
  - ⚠️ **Refuted (0-3): that chatterbox-mlx is shown to fit a 24 GB M4.** Fit is **unmeasured** for every tool.
    Individual model weights carry their own licences — check before client use.
  - **Kokoro does not clone voices.**
- **Kildall fit:** **Phase 9.3 / 9.10** — a cloned voice per profile. Also a candidate for the **missing
  Vietnamese voice** (Qwen3-TTS via mlx-audio). Gate: measured RAM next to Lane A, and a quality check.

## 6. Kimi Agent Swarm — ✅ confirmed from Moonshot's model card (checked by hand)

- **What:** the model breaks a task into parallel, specialised subtasks — **up to 300 sub-agents and 4,000
  coordinated steps** ([Kimi-K2.6 card](https://huggingface.co/moonshotai/Kimi-K2.6)). Introduced with K2.5,
  scaled in **K2.6 (2026-04-14)**.
- **Model:** **~1.03 T total / 32 B active** MoE, 384 experts, **open weights, "Modified MIT"** licence
  (Hugging Face API: `license: other, modified-mit`).
- **Vendor benchmarks:** BrowseComp **83.2% → 86.3% with Agent Swarm** · HLE-Full with tools 54.0% ·
  DeepSearchQA F1 92.5% · OSWorld-Verified 73.1%.
- **Pricing (secondary sources):** API $0.95 in / $4.00 out per M tokens; kimi.com plans $19 / $39 / $99 / $199
  per month, with Agent Swarm on the higher tiers.
- ⚠️ **The weights are open; the swarm orchestration on kimi.com is not.** Running the model locally does not
  give you the 300-agent runtime.
- **Kildall fit:** K2.6 is a **Lane C** model (32 B active × 0.5 B/param ≈ 16 GB per token read → roughly
  **5–6 s/token** off Thunderbolt 4 — arithmetic, not measured). Kildall already plans **Kimi K3** in Lane C.
  The swarm *pattern* belongs to **Phase 4.4 subagents**, capped by free RAM — 300 parallel agents is impossible
  on 24 GB.

---

## What this means for Kildall

1. **No new phase is needed.** Every feature maps onto a planned slice: council → 7 / router · command mode →
   9.3 + 4C · ultrareview → 4.4 · Grok Bot → 3–4 + 4C + 9.2 · cloning → 9.3/9.10 · swarm → 4.4 + Lane C.
2. **The one new build item is voice cloning** via mlx-audio or chatterbox-mlx — worth adding to 9.3/9.10, and it
   may also solve the missing Vietnamese voice.
3. **Two patterns worth copying exactly:** Model Council's *"show where models agree and differ"* output, and
   Ultrareview's *"reproduce each finding before reporting it"* rule.

## Open questions *(not answered by this research)*

- Do mlx-audio's cloning models run within 24 GB next to a resident Lane A, and how close are they to
  ElevenLabs on similarity?
- Can the llm-council three-stage pattern point at local llama.cpp / MLX servers, and is a local council worth
  its latency against one stronger model?
- Grok Bot's standalone price, and whether it reaches email, Slack or Telegram — only secondary sources so far.
- A local open equivalent to Ultrareview's verify loop and to Wispr Command Mode — none found.

## Sources

**Primary:** [Perplexity — What is Model Council](https://www.perplexity.ai/help-center/en/articles/13641704-what-is-model-council) ·
[Perplexity — Introducing Model Council](https://hub-prod.perplexity.ai/hub/blog/introducing-model-council) ·
[Wispr — Command Mode docs](https://docs.wisprflow.ai/articles/4816967992-how-to-use-command-mode) ·
[Anthropic — Ultrareview docs](https://code.claude.com/docs/en/ultrareview) ·
[xAI — Introducing Grok Bot](https://x.ai/news/introducing-grok-bot) ·
[xAI — Grok Bot in more plans](https://x.ai/news/grok-bot-more-plans) ·
[ElevenLabs — PVC docs](https://elevenlabs.io/docs/eleven-creative/voices/voice-cloning/professional-voice-cloning) ·
[ElevenLabs — pricing](https://elevenlabs.io/pricing) ·
[Moonshot — Kimi-K2.6 card](https://huggingface.co/moonshotai/Kimi-K2.6)
**Open source:** [karpathy/llm-council](https://github.com/karpathy/llm-council) ·
[Blaizzy/mlx-audio](https://github.com/Blaizzy/mlx-audio) · [chatterbox-mlx](https://pypi.org/project/chatterbox-mlx/)
**Secondary:** [lumienai — Model Council in Computer](https://lumienai.com/news/perplexity-model-council-computer-multi-model-queries) ·
[Vellum — Grok Bot breakdown](https://www.vellum.ai/blog/official-grok-bot-breakdown) ·
[MarkTechPost — Kimi K2.6](https://www.marktechpost.com/2026/04/20/moonshot-ai-releases-kimi-k2-6-with-long-horizon-coding-agent-swarm-scaling-to-300-sub-agents-and-4000-coordinated-steps/) ·
[OpenRouter — Kimi K2.6](https://openrouter.ai/moonshotai/kimi-k2.6)

## Change log

- **2026-10-01** — Created. The first research run stopped when 28 of 106 agents hit a session limit; the
  resumed run completed all 106. Grok Bot and Kimi Agent Swarm were verified by hand because the research
  budget did not reach them. Quota-failed results were not merged as fact.
