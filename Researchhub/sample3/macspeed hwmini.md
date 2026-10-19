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

### Gaps found (code at `main` 29ab89b, logs in `code/.session/`)
1. **`kildall.py:508` (`stream_reply`) and `subagents.py:328` send `cache_prompt=False`.** Every answer turn and every
   tool round re-reads the full prompt. Only the router reuses its prefix. The cache was turned off on 2026-09-08
   for RAM; it was later bounded, but these two paths were never switched back.
2. **`kildall.py:488` (`fit_messages`) puts recalled memory inside the system message, at the top of the prompt.**
   Recall changes per turn, so nothing after it can match. Same pattern as the Claude Code attribution header.
3. **Cost is visible already:** real-child soak p50 **24.7 s** for 64-token replies (Phase 4.4). Writing 64 tokens takes
   ~2–5 s, so most of that wait is reading. *(Inference from recorded numbers.)*
4. **SWA re-reads already happen on the router:** `.session/lane_a.log` (Oct 14) has **10** `forcing full prompt
   re-processing` lines in ~2,251 prompt starts, all slot 0, ~3.8K-token prompts. Gemma's SWA window is **1,024**
   and the only checkpoints sat at ≤223 tokens. Requests with `cache_prompt=False` never try reuse, so they re-read
   silently and never show this line.
5. **4K trimming** (`previous.pop(0)`) shifts the whole history = full re-read, like compaction. Rarer at larger context.

### Proposed slice — "answer-path prompt reuse" (not in the plan yet)
- `cache_prompt=True` on `stream_reply` and subagents; keep answer slots 1–2 pinned.
- Append-only prompt: stable system + tools first; recalled memory moves below the stable part (exact place: spec decides,
  since SWA can only rewind to a checkpoint).
- Log `timings.cache_n` vs `prompt_n` per request (llama-server already returns them) → cache-hit % in health.
- One session at higher log verbosity; count `forcing full prompt re-processing`.
- **Risks:** llama.cpp warns reused cache may not be bit-identical to a fresh read, so temperature-0 gates can shift —
  rerun every gate, frozen fixtures untouched · checkpoint count may need tuning (`--swa-full` keeps the full SWA cache,
  more RAM — mini PC only) · memory-pressure soak must still pass.
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

### Other ideas
- **Per-skill thinking-effort cap** for thinking models (Lane B/C, NIM): `xhigh` = 5.5× tokens.
- **Bench reports first-token time and the prefill/decode split** per request, not only tok/s.

---

## Not verified
- All video numbers are the creator's, citing user reports, X posts and the Lithos repo study. No `/deep-research` run;
  none checked against primary sources.
- Names come from auto-captions and may be misspelt ("Deep Spark"/"Dispark" = DSpark, "Llama Metal" = Lithos Metal,
  "AgentPerf Local", "MLTF").
- Kildall facts above are checked against code at 29ab89b, BENCHMARKS.md and `.session/lane_a.log`.

## Change log
- **2026-10-19** — Created from both videos; Kildall gaps checked in code and logs.
