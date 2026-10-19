# macspeed hwmini — what "200 tok/s" really means, and why local agents feel slow

**Sources:** two videos by Kai (YouTube), watched 2026-10-19 from native captions (no Whisper):
- [L7noXCBSObc](https://www.youtube.com/watch?v=L7noXCBSObc) — *"Qwen 3.8 27B Just Hit 200 Token/s on Mac M5 (Lithos Metal)"*, 19:46
- [x_qmqqp6d7s](https://www.youtube.com/watch?v=x_qmqqp6d7s) — *"Why Your Mac Is Slow at Local AI (And It's Not the Chip)"*, 15:05

**Related:** `dflash2 hwmini.md` (speculative decoding on Metal), `qwen38-27b hwmini.md` (the 27B model itself).

---

## ⚡ ANSWER FIRST

| Question | Answer |
|---|---|
| **Can this improve Kildall's pace?** | ✅ **Yes — through prompt reuse, not speculative decoding** |
| **Biggest win** | Turn prompt reuse on for the answer and subagent paths; move recalled memory out of the top of the prompt |
| **Speculative decoding on the M4** | ❌ No. Metal already measured a loss; Lithos tunes only the M5 Max 40-core |
| **Speculative decoding on the mini PC** | ⚠️ Maybe, for code/math skills only. Measure |
| **Install Lithos Metal?** | ❌ No. Metal only, one request at a time, temperature-0 drift bug, 11 days old |

**Verdict:** both videos say the same thing from two sides. Speed headlines measure *writing*;
agent work is mostly *reading*. Kildall already proved this on its router (0.79 s warm vs 16.4 s cold),
but the answer and subagent paths still re-read their whole prompt every round.

---

## Video 1 — the "200 tok/s" headline

**The ceiling.** Writing speed ≤ memory bandwidth ÷ model bytes.
M5 Max 40-core: 614 GB/s ÷ 16 GB (27B, 4-bit) ≈ **38 tok/s**. Measured plain decode: **30.5** (≈80%).
Same family, different ceilings: M5 Max 32-core 460 GB/s · plain M5 153 GB/s · M6 Mac mini 170 GB/s (≈10 tok/s for this model).

**Above the ceiling = speculative decoding only.** A 1.1 GB drafter ("DSpark") guesses 7 tokens; the 27B checks
all of them plus 1 in one weight read (8 rows per memory trip). All right = 8 tokens; first guess wrong = 1 token
*plus* the drafting cost. Technique from a DeepSeek paper (July): 60–85% faster per user on DeepSeek's servers.

**What the numbers really were:**

| Claim | What it is |
|---|---|
| 200 tok/s (blog, Oct 8) | No context, prompt or acceptance rate given |
| 168 @ 128 ctx / 127 @ 32K (README) | **Projection**: assumes 6 of 8 accepted, excludes drafting, checking, rewind — "not measured end-to-end" |
| **≈80 tok/s** (repo study, Oct 3) | **Measured**: 4 prompts (code/math/chat/text), ~150 rounds, **2.5 accepted per round** |

**Text type decides the gain** (code repeats; prose does not):

| Test | Code | Prose / chat |
|---|---|---|
| Lithos vs oMLX, M5 Max 40c 128 GB, 3 runs | **59 vs 55** · at 32K: **49 vs 39 (+25%)** | **34 vs 38 (slower)** |
| MLX DSpark, M4 Pro | math **3×**, code **2.4×** | chat **<2×** |
| Lithos untuned fallback, M4 Pro | — | **2 tok/s with drafting vs 7 without** |

**Reading speed sinks it for agents.** Lithos prefill 374 tok/s on a 4K prompt vs oMLX 948; a 16K prompt
starts after 43 s vs 17 s. AgentPerf Local replay (Qwen 3.8 27B, 8 tasks, 168 turns): **196K tokens read vs
31K written (6:1) even with caching** — total ~18 min on Lithos vs ~13 min on oMLX. Prefill fixes are merged, not released.

**Three kinds of tok/s:** peak (one prompt), sum (MLTF "200+" = 4 requests added; one user got 70),
copy (RTX 3090 "381" = copying a 25K document back, 15/16 accepted; normal chat 133).

**Lithos limits:** tuned kernels for the M5 Max 40-core only; M4 Max, M5 Pro (27B) and M5 Max 32-core get an
unmeasured fallback (no megakernels, matrix accelerator off); no M6 backend; one generation at a time
(second request = HTTP 429); a bug report (Oct 14) shows drafted output drifting from plain output at
temperature 0 — a correctness bug; repo 11 days old, 35 open issues/PRs.

**Thinking cost:** Qwen `xhigh` effort = **5.5×** the tokens of thinking-off. "The fastest token is the one never written."

**Three questions for any speed headline:** what was counted (peak, average, sum, projection)? what was written
(code, prose, math, copy)? how long did the whole task take, from Enter to done?

---

## Video 2 — prefill, and what breaks the prompt cache

**Two jobs.** Prefill = reading the prompt. Decode = writing. The tok/s counter shows decode only.
M1 Max: counter said 57 tok/s; with 8,500 tokens of context the real speed was **3 tok/s** — prefill was **94%** of the wait.

**Prefix caching** = the server keeps what it already read and skips it if the next prompt starts the same.
M5 Pro 64 GB, Qwen 3.8 27B: 158K context, 157.6K cached, 400 new → first word in **6.1 s**. A few turns later:
188K context, only 147K matched, 41K re-read → **268 s**. Same Mac, model and session: **44×**. No chip closes 44×.

**What breaks the cache:**
1. **A changing token at the top of the prompt.** Claude Code (Mar–Jun) put a per-request attribution block first;
   Anthropic's servers strip it, local servers do not, so every turn was a cold read. Fixed in v2.1.x.
2. **Context too small.** Ollama sizes context from visible GPU memory (<24 GB → 4K, 24–48 GB → 32K, >48 GB → 256K);
   a Mac GPU sees ~¾ of RAM. Claude Code's first request is ~33K tokens, so a 48 GB Mac starts full, compacts
   again and again, and every compaction is a cold read. Ollama's own docs say ≥64K.
3. **Hybrid / sliding-window layers.** These keep a running state that cannot rewind to any point. The server
   saves checkpoints thousands of tokens apart; if the prompt changes far from a checkpoint, it re-reads from zero.
   llama.cpp logs `forcing full prompt re-processing` — only at a higher log level than the default.
4. **The front end.** Same server and model: Hermes cached normally, OpenClaw showed **0** cached tokens.
5. **Stripping thinking tokens** between turns changes the history and breaks the cache from that point.

**The chip still matters for reads you cannot skip** (first look at a repo): M5 Pro + Claude Code waited >3 min
(55–70K tokens) for the first word. A 32K cold read on a 27B: 5–11 min on M1 Max, ~40 s on M5 Max;
M5 prefill ≈ 3.6× M4 Max on llama.cpp. *"The cache decides how many cold reads you pay for; the chip decides what each costs."*

**Checklist:** update the agent tool · check the real context size · raise log level and search for
"full prompt re-processing" · watch the cached-token counter (0 deep in a session = red flag) · lower thinking effort.

---

## What this means for Kildall

### Already done
- **Router:** slot 0 pinned, 3,863-token prefix kept warm, `cache_prompt=True`. First route **0.79 s warm vs 16.4 s cold** (BENCHMARKS.md, router warmth) — the video's lesson, already measured here.
- **Bounded cache:** `--cache-ram 768 --ctx-checkpoints 3` (replaced the 8 GB server prompt cache that caused the 2026-09-08 RAM failure).
- **Resident thinking off** (`--reasoning off`), so no thinking-strip break. **Explicit `-c 4096`**, so no Ollama default trap.
- **Gates time whole requests** (p99), not tok/s.

### Gaps found (code at `main` 29ab89b, logs in `code/.session/`; deep-checked 2026-10-19)
1. **`kildall.py:508` (`stream_reply`) and `subagents.py:328` send `cache_prompt=False`.** In pinned llama.cpp
   (`server-context.cpp`, b10809 copy in `.session/phase4.4-20260927/audit/upstream/`) that sets `n_past = 0`:
   every answer turn and every tool round (up to 8 per turn) re-reads the full prompt. Only the router reuses its
   prefix. **Origin:** commit 767bb25 (2026-09-06, "reproducible Lane A gate checks") — set for repeatable gates;
   commit 3149863 (2026-09-09) copied it into the CLI. *Not* the 2026-09-08 RAM fix (`--cache-ram`, a separate setting).
2. **`kildall.py:488` (`fit_messages`) puts recalled memory inside the system message, at the top of the prompt.**
   Recall changes per turn (and mid-turn via the `recall` tool), so nothing after it can match. Same pattern as the
   Claude Code attribution header.
3. **Measured cost:** `.session/lane_a.log` (Oct 14), answer slot 1: 53 requests, **345 s reading vs 28 s writing —
   92% of slot time is reading**; mean prompt 1,436 tokens, mean reply 14 tokens; **0** reuse events on slots 1–2.
   Real-child soak p50 **24.7 s** for 64-token replies (Phase 4.4) fits the same picture.
4. **RAM for reuse is already paid and thrown away:** work slots create two SWA checkpoints per request
   (**106–113 MiB each**), then the next request erases them (`pos_next = 0`). 16K test: slot 1 got a prompt sharing
   8,192 of 16,383 tokens with its cache (`sim = 0.500`) and re-read all of it (~73 s).
5. **Correction:** the 10 `forcing full prompt re-processing` lines on slot 0 are **not** SWA failures. Slot 0 held a
   different 229-token prompt; the new one shared 4 of 3,816 tokens (`sim = 0.001`). A full read was correct.
6. **4K trimming** (`previous.pop(0)`) drops the oldest message once full, which changes the prompt right after the
   system part = full re-read, like compaction. With ~1.4K-token prompts at 4K this starts after a few turns.
7. **Children share slot 1:** `turn_slot` gives every turn the first work slot; children borrow it while the parent
   waits, so the parent's cached prefix is overwritten and its next round re-reads.

### How reuse will behave (derived from the pinned source)
- llama.cpp keeps checkpoints at **the start of the last user message** and **4 and 132 tokens before the prompt end**
  (`-ub 128`); min spacing 8,192. Gemma SWA window **1,024**.
- **Tool rounds inside a turn:** prompt only grows at the end → reuse works (direct, or from the near-end checkpoint).
  Only the reply + tool result are read.
- **Next turn, memory at the top:** change point has no checkpoint before it → full re-read. **Memory placed with the
  current user message** → change point lands at the last-user checkpoint → only the last turn is re-read.
- **Trimming one message at a time** keeps breaking the prefix; trimming a large chunk at once (e.g. half the history)
  keeps it stable for several turns.

### Proposed slice — "answer-path prompt reuse" (not in the plan yet)
- `cache_prompt=True` on `stream_reply` and subagents; keep answer slots 1–2 pinned.
- Append-only prompt: stable system + tools first; recalled memory moves next to the current user message (lands on
  llama.cpp's last-user checkpoint).
- Trim history in large chunks, not one message per request.
- Log `timings.cache_n` vs `prompt_n` per request (llama-server already returns them) → cache-hit % in health.
- Optional, same gate rerun: system prompt still says "You are Orbi" — kept on purpose in the rename to avoid gate drift.
- **Risks:** llama.cpp README (pinned, line 589): reused cache "can cause nondeterministic results" — temperature-0 gates
  can shift; rerun every gate, frozen fixtures untouched. Partial comfort: the router already runs `cache_prompt=True`
  and routing holds 20/20 · memory-pressure soak must still pass (checkpoint RAM is already paid today) ·
  `--swa-full` keeps the full SWA cache (more RAM — mini PC only).
- **Expected gain (estimate, unmeasured):** a full 4K re-read costs ~16 s on the M4 (measured router rebuild 15.8 s for
  3,863 tokens). With reuse, tool rounds and repeat turns read only new tokens. On the mini PC at 32K+ this decides
  usable vs not: a cold 32K read is ~30–70 s at the community 460–1,000 tok/s prefill numbers.

### Speculative decoding
- **M4:** no. llama.cpp on Metal measured −11% to −28% even at 100% acceptance (`dflash2 hwmini.md`). Lithos gives the M4
  an untuned fallback (one M4 Pro report: 2 vs 7 tok/s). MLX DSpark runs on M4 Pro but needs a drafter for the exact
  target model — none checked for Gemma 4 26B-A4B.
- **Mini PC:** already planned as "measured per platform". **New from this video:** Kildall routes per skill, so drafting
  can be on only for code/math leaves and off for prose/chat, where it can lose. Measure acceptance per skill class, and
  time whole tasks, not tok/s.
- **MoE caution (inference, unmeasured):** the resident model is MoE (4B active). Checking 8 tokens can touch more
  experts than 1, so the gain is likely smaller than on a dense 27B.

**Web check (2026-10-19):**
- **Strix Halo (the mini PC chip), llama.cpp Vulkan:** Gemma 4 31B dense Q8 + Gemma 4 E2B drafter: **6.18 → 12.55 tok/s
  (+103%)** average; math +170%, code +139%, creative +40%. Best `--draft-max 4`, `--parallel 1`. Acceptance 35–62%.
  26B-A4B variants configured but **not benchmarked**. ([sleepingrobots](https://sleepingrobots.com/dreams/speculative-decoding-gemma4-strix-halo/))
- **Not byte-identical in practice:** Qwen 3.8 27B on RTX 3090, llama.cpp MTP: +60% speed, but **92–100%** of outputs
  differed from plain greedy at a 1,600-token cap; cause not established. Kildall's temperature-0 gates must decide.
  ([hackmd study](https://hackmd.io/@thc1006/qwen3-8-27b-speculative-decoding-rtx-3090))
- **DSpark is real** (DeepSeek + Peking University): 60–85% faster per user on V4-Flash. **Gemma 4 DSpark drafters exist
  in vLLM, Modular MAX and NVIDIA NeMo — not llama.cpp.** ([AlphaSignal](https://alphasignalai.substack.com/p/how-dspark-speeds-up-llm-inference),
  [vLLM](https://docs.vllm.ai/en/stable/api/vllm/model_executor/models/gemma4_dspark/))
- **Apple via MLX, not llama.cpp:** MTPLX (MLX + native MTP) on M4 Max 64 GB: Qwen3.6-27B 4-bit **41.6 vs 24.3 tok/s (1.71×)**.
  Needs a model with an MTP head. ([MTPLX notes](https://instagit.com/youssofal/MTPLX/performance-benefits-mtplx-m4-m5-max-chips.md))
- **Lithos Metal:** no trace found on the web. Its "200 tok/s" stays unverified.

### Other ideas
- **Per-skill thinking-effort cap** for thinking models (Lane B/C, NIM): `xhigh` = 5.5× tokens.
- **Bench reports first-token time and the prefill/decode split** per request, not only tok/s.

---

## Not verified
- Video numbers are the creator's, citing user reports, X posts and the Lithos repo study. Only the speculative-decoding
  claims above were web-checked (secondary sources); the rest are unchecked. No `/deep-research` run.
- Names come from auto-captions and may be misspelt ("Deep Spark"/"Dispark" = DSpark, "Llama Metal" = Lithos Metal,
  "AgentPerf Local", "MLTF").
- Kildall facts above are checked against code at 29ab89b, BENCHMARKS.md and `.session/lane_a.log`.

## Change log
- **2026-10-19** — Created from both videos; Kildall gaps checked in code and logs.
- **2026-10-19 (deep check)** — Traced the turn loop, slots and pinned llama.cpp source. Corrected two claims (origin of
  `cache_prompt=False`; slot-0 events are not SWA failures). Added the measured 92% read share, wasted checkpoint RAM,
  4K trimming and slot-sharing risks, and web checks of the speculative-decoding claims.
