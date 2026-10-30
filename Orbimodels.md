# Orbimodels — The Explicit Model List

**v1 · 2026-09-05.** The concrete answer to "which models, how big, how much disk." *(Product renamed Kildall 2026-09-27; model list unchanged.)*
Replaces the soft "~26 models, ~4.9 TB" in `Orbiplan.md`. **Every number here sums.**

---

# ⚡ ANSWER FIRST

| | |
|---|---|
| **Models** | **22** |
| **Params STORED** | **~9.87 T** |
| **Disk at 4-bit** | **~5.23 TB** of the 8 TB drive |
| **Held in RAM at once** | **~5–8 GB** — Lane A streams its experts; only ~3 GB of it is ever active |
| **Fits the M4 24 GB?** | ✅ **yes**, with one caveat — see the RAM ceiling warning |

**Quant assumption:** 4-bit ≈ **0.5 bytes/param**, so GB ≈ params(B) ÷ 2. Kimi K3 is the exception —
its 1.7 TB is the project's own measured figure (1.56 TB checkpoint + 109 GB packed trunk), not a
calculation.

## ⚠️ RAM ceiling

**Lane A streams.** 90 GB on disk, ~3 GB of experts active per token, plus the dense trunk and KV
cache — call it **5–8 GB resident**. That leaves room for one Lane B specialist alongside.

**The one pair that still does not fit:** Lane A + `Qwen3-Omni` (15 GB) is over budget. Use the
**ASR + TTS pair (2.0 GB)** for voice — better per-task scores anyway.

**Quantise the KV cache** (`-ctk q8_0 -ctv q8_0`) and cap context at 32K. Past ~100K tokens the cache
outgrows the active weights.

---

# LANE A — resident router · **MoE, no size cap**

## The two rules that decide this

1. **Sparse when resident — but dense is convertible, not disqualified.** The architecture rests on
   sparsity. A dense model fires every parameter every token, which a 24 GB machine cannot afford at
   scale — **but a dense model can be converted to MoE with CMoE in under five minutes, no training.**
   See **"When a model is dense — convert it"** below for the real quality cost. Prefer a native MoE;
   convert a dense one rather than rejecting it.
2. **No size cap.** Total params are nearly free — they live on disk. **Active params are the cost.**
   Pick on active size and quality, never on total.

> ❌ **Retracted:** earlier versions of this file capped Lane A at ~5 GB / 8B, then picked
> **Qwen3.8-27B — a dense model.** Both were wrong. The cap was invented so a Lane B model could sit
> in RAM beside Lane A; the dense pick contradicted the plan's own premise. Neither came from a
> requirement.

## The candidates — all four are live

**Ranked. Phase 1 measures and picks.** Disk is against **253.65 GB free** (measured 2026-09-06).

**Why Lane A is sized against the internal disk, and only Lane A:** Lane A **streams its experts on
every request**, so disk read speed sets tok/s directly. Your internal SSD is a **measured 3.44 GB/s**;
external Thunderbolt is slower. **Lane A lives on the internal disk permanently** — not as a stopgap.
It also has to run before the 8 TB drive exists.

**Lanes B and C are sized against the external drive**, not this one. Disk column below is internal
free space: **93.3 GB now, ~155 GB once the Trash is emptied.**

| # | Model | HF path | Shape | Active | Disk @4-bit | Fits? | Licence | Tool use | The catch |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **Qwen3.8-Flash-Next** | `Qwen/Qwen3.8-Flash-Next` | **native MoE** 180B | **6B (3.3%)** | **~90 GB** | ✅ **fits, 163 GB spare** | **Apache-2.0** | strong | **No conversion, so zero quality loss.** Multimodal. Speed unmeasured — no published tok/s for a 180B/6B MoE on M4 |
| **2** | **Qwen3.8-27B + CMoE** | `Qwen/Qwen3.8-27B` | dense **→ converted to MoE** | ~7B @25% | **~17 GB** | ✅ | **Apache-2.0** | strong | Native vision, tiny footprint. But **conversion costs quality** — 33–65% worse perplexity training-free, or ~1 hr LoRA to recover ~76%. **CMoE on Metal unverified** |
| **3** | **Gemma 4 26B-A4B** | `google/gemma-4-26b-a4b` | **native MoE** 26B | **4B** | **~13 GB** | ✅ | Gemma Terms | ⚠️ **weak** | **Only one proven on Apple Silicon** — 25–36 tok/s on M4 Pro via Turbo Fieldfare. But weak at tool use, Lane A's whole job |
| **4** | **Granite 4.1 8B** | `ibm-granite/granite-4.1-8b` | dense, convertible | 8B | **~4.3 GB** | ✅ | Apache-2.0 ⚠ | ✅ **best <10B** | Smallest, safest. **Proven floor — 19.5 tok/s effectively measured.** If nothing clears the gates, this ships |

**Why #1 leads:** it fits today, keeps a **native vision encoder** (Lane A reads screenshots and video
itself), and is Apache-2.0. **Why #2 could still win:** no conversion at all, so no quality loss. It now fits — but at 90 GB of
93.3 GB it leaves 3 GB, so nothing from Lane B could sit beside it.

**#1 and #2 are both Qwen 3.8**, so switching between them is a config change, not a redesign.

## ✅ MEASURED ON YOUR MACHINE — 2026-09-06

**`qwen3:8b` (8B dense) → 19.48 tok/s.** Prompt eval 100 tok/s, load 4.1 s. First real number from
this M4, not an estimate.

**What it implies.** 8B dense clears 15 tok/s with ~30% headroom, so the **active-parameter budget for
Lane A is roughly ≤ 10 B active**. Every MoE candidate sits under it:

| Candidate | Active | Projected from the 19.48 anchor | Verdict |
|---|---|---|---|
| Gemma 4 26B-A4B | **4B** | comfortably above 19 tok/s | ✅ |
| Qwen3.8-Flash-Next | **6B** | ~20–25 tok/s **if streaming holds** | ✅ likely |
| Qwen3.8-27B + CMoE @25% | **~7B** | near or above 19 tok/s | ✅ likely |
| Granite 4.1 8B | 8B dense | **~19.5 tok/s — effectively measured** | ✅ **proven** |
| ~~Qwen3.8-27B dense, unconverted~~ | 27B | **~5.8 tok/s** | ❌ **would fail — confirms the conversion is required** |

**The dense-27B rejection is now backed by a number, not just architecture.** And **Granite 4.1 8B is
a proven-viable floor** — whatever else fails, Lane A ships.

⚠️ **Still unmeasured: streaming.** The 19.48 figure is a model that fits in RAM. Nobody has measured a
180B/6B MoE paging experts from SSD on an M4. That remains Phase 1's first test.

## Phase 1 gates

1. **tok/s over mmap streaming** — **> 15**. ⚠️ **The unknown. Test this first, before anything else**
2. **Routing accuracy** — right skill of 341? **≥ 18/20**
3. **Tool-call validity** — callable JSON every time? **20/20**
4. **RAM under load** — watch memory pressure for **10 minutes, not 60 seconds**

---

# LANE B — hot-swap specialists

**14 models · ~134 B params · ~69 GB · one loaded at a time**

| Job | Model | Params | Disk | Licence | Evidence |
|---|---|---|---|---|---|
| **ASR** (speech in) | `nvidia/canary-qwen-2.5b` | 2.5B | **1.4 GB** | ⚠ | **Tops HF Open ASR — 5.63% WER** |
| ASR, local *(Phase 9.3)* | **`SYSTRAN/faster-whisper`** — Whisper model size picked in 9.3 | — | **~0.8–1.6 GB** | MIT | 🔄 **Swapped in 2026-09-27, user choice.** ⚠️ **CPU-only on Mac (no Metal)** — gated on end-of-speech → first audio < 1.5 s; fallback `mlx-whisper`/`whisper.cpp`. Replaces `Qwen/Qwen3-ASR-1.7B` (kept as fallback: 52 languages)
| **TTS** (speech out) *(Phase 9.3)* | **`hexgrad/Kokoro-82M`** via `kokoro-mlx` | 82M | **~0.35 GB** | Apache-2.0 | 🔄 **Swapped in 2026-09-27, user choice.** MLX, 54 voices. ⚠️ **No Vietnamese voice** in its language list — keep `Qwen/Qwen3-TTS-12Hz-1.7B` as fallback for languages Kokoro lacks (check it covers Vietnamese before relying on it)
| Voice, single-model | `Qwen3-Omni-30B-A3B` ⚠ | 30B / 3B act | **15 GB** | ⚠ | Latest Omni. ⚠️ **Too big to co-load — use the ASR+TTS pair (2.4 GB)** |
| **OCR / documents** | `PaddlePaddle/PaddleOCR-VL-1.6` | 0.9B | **0.5 GB** | ⚠ | ✅ **Current — 28 May 2026.** 96.33% OmniDocBench v1.6, open OCR leader; beats models hundreds of times its size |
| **Embeddings** (memory) | `microsoft/Harrier-oss-v1-27B` | 27B | **13.5 GB** | **MIT** | ✅ **#1 on multilingual MTEB-v2**, the newer benchmark — 30 Mar 2026. 100+ languages, 32k context. Beats `Qwen3-Embedding-8B` (#1 on the older MTEB at 70.6) |
| Rerank (memory stage 2) | `Qwen/Qwen3-Reranker-4B` | 4B | **2.2 GB** | Apache-2.0 ⚠ | ✅ **4B beats the 8B on MTEB-R — 69.76.** The 8B only leads on Chinese (CMTEB-R 77.45). **Half the size, better score** |
| Embeddings, **fast path** | `microsoft/Harrier-oss-v1-0.6B` | 0.6B | **0.35 GB** | **MIT** | nDCG@3 **0.8911** vs Qwen3-Embedding-0.6B's 0.8168. **Use when 13.5 GB is too heavy** — same family, same tokenizer. (270M variant also exists) |
| ✅ **Prompt-injection guard** | `ibm-granite/granite-guardian-4.1-8b` · Ollama `granite4.1-guardian` | 8B | **4.3 GB** | Apache-2.0 ⚠ | **Leads prompt-injection + hallucination** — beats Llama Guard, which misses patterns Granite catches. **April 2026**, adds Bring-Your-Own-Criteria. This is Phase 3's guard |
| Translation | `xiaomi-research/MiLMMT-46-12B` | 12B | **6.5 GB** | ⚠ | ✅ **Current** — Gemma3-based, 46 languages, arXiv Feb 2026. Best on WMT24++ and FLORES+ |
| **Image gen** | `Qwen/Qwen-Image-2512` | 20B | **10 GB** | **Apache-2.0** | ✅ **Weights shipped, Apache-2.0, free commercial use.** Supersedes `Qwen-Image` — realistic humans, natural detail, accurate text rendering |
| **Video gen** | **Wan 2.7** — **ModelScope**, not HF | 27B / 14B act | **13.5 GB** | Apache-2.0 | MoE diffusion transformer. ⚠️ **Wan 3.0 shipped 6 Aug 2026** — native 30-second 1080p with audio, but **public beta**. Budget uses 2.7; **re-decide at Phase 5** |
| 3D gen | **`tencent/Hunyuan3D-2.1`** | 5.3B | **2.7 GB** | ⚠ | First open model with full PBR texture weights. ⚠️ **v2.5 and v3 both shipped in 2026** (v2.5 cut latency 25%) — sizes unpublished, so budget uses 2.1. **Re-pick at Phase 5** |
| ✅ **Visual grounding / pointing** | `allenai/Molmo2-8B` ⚠ path | 8B | **4.3 GB** | Apache-2.0 ⚠ | **Beats Gemini 3 Pro on video pointing — 38.4 vs 20.0 F1.** Replaces Molmo-72B at **1/9 the size**. Alt: **Moondream 3** (9B MoE, **2B active**, purpose-built for detection + pointing, but Preview) |

**Three things to act on:**
1. ✅ **Guard is current** — `granite-guardian-4.1` (April 2026) replaced 3.x on 2026-09-06.
2. ⚠️ **8 of 13 licences are unconfirmed.** Open each model card before installing.
3. **Wan 2.7's official weights are on ModelScope** — HF copies are community re-uploads.
4. ⚠️ **Two newer versions exist but are unbudgeted** — **Wan 3.0** (beta) and **Hunyuan3D v3**. Both
   have unpublished sizes, so the totals below use the stable 2.7 / 2.1 releases. **Phase 5 decides.**

**Lane B belongs on the external drive.** It has no streaming-speed argument — a specialist loads,
runs for seconds, and unloads. Until the drive arrives, install selectively on the internal disk: the
**voice pair + OCR + embeddings come to under 8 GB** and cover most of Phase 5.

**Lane B subtotal: 14 models · ~149 B params · ~76 GB.**

**On Qwen versions here:** `Qwen3-ASR`, `Qwen3-TTS`, `Qwen3-Embedding`, `Qwen3-Reranker` and
`Qwen3-Omni` are **the latest of their lines** — Qwen 3.8 shipped only three models (27B, Flash-Next,
2.4T-A95B) and none of them replaces a specialist. **Re-check each when Qwen ships a 3.8 equivalent.**

---

# LANE C — giants, streamed

**7 models · ~8.9 T params · ~4,750 GB · ⏸ ALL gated on the 8 TB drive, 1+ month out**

| # | Job | Model | Params | Active | Disk | Licence | Why it earns the space |
|---|---|---|---|---|---|---|---|
| 1 | **Agentic coding** | `moonshotai/Kimi-K3` | **2.8 T** | 104B | **1,700 GB** | Custom *Kimi K3* | Largest open model. **#1 tool-calling and Frontend Code Arena.** 93.4% SWE-bench Verified (Vals AI independent harness) |
| 2 | General, long-context | `Qwen/Qwen3.8-2.4T-A95B` ⚠ | **2.4 T** | 95B | **1,200 GB** | ⚠ | Second-largest open model. **Text-only** |
| 3 | **Backend / algorithmic** | `deepseek-ai/DeepSeek-V4-Pro-0813` ✅ | **1.6 T** | 49B | **800 GB** | **MIT** | **80.6% SWE-bench Verified — top open score on the official board.** GA 13 Aug 2026, MIT |
| 4 | **Math + reasoning** | `zai-org/GLM-5.2` | **753 B** ✓ | ~40B | **376 GB** | **MIT** | **99.2 AIME 2026, 91.2 GPQA Diamond** — best open math reasoning |
| 5 | Tool calling | `zai-org/GLM-5.3` | **744 B** | ~40B | **372 GB** | Custom *GLM-5.3* | **#2 tool calling (35.4).** 200K ctx |
| 6 | Cheap reasoning | `zai-org/GLM-5.3-Flash` | **320 B** | 18B | **160 GB** | **MIT** | Shipped ahead of the flagship |
| 7 | Cheap coding | `deepseek-ai/DeepSeek-V4-Flash-0731` ✅ | **284 B** | 13B | **142 GB** | **MIT** | 79.0% SWE-bench Verified at **1/6 the size** of V4-Pro. Production release 31 Jul 2026 |
| 7b | Cheap coding — **newest** | `deepseek-ai/DeepSeek-V4.1-Flash` ✅ (2026-09-10) | **763 B** (HF API) | ⚠️ unpublished here | **~380 GB @4-bit** | **MIT** | 🔄 **Latest DeepSeek Flash (added 2026-10-13).** Too big for a 128 GB machine (~286 GB even at 3-bit), but **v54 (2026-10-30): fits the reward server's 512 GB RAM + 64 GB VRAM** — a resident candidate there, speed unmeasured. Until then: **NVIDIA NIM** (live 2026-10-13; ⚠️ slice 5c on 2026-10-24: timed out once at 30 s, not qualified) or Lane C. ⚠️ HF API puts V4-Flash-0731 at **304 B**, not the 284 B above |
| 8 | ⚠️ **Reasoning + tools** | `tencent/Hy4-preview` ⚠️ **PREVIEW** | **770 B** | **49B** | **385 GB** | **Apache-2.0** | **SWE-Bench Pro 65.7 · GPQA Diamond 92.3 · Deep SWE 64.3 · Toolathlon 74.1.** 256 routed + 1 shared expert, top-8/token, 78 layers, 1M ctx, text-only. Ships a **built-in MTP layer** for speculative decoding. 🔴 **No GGUF or MLX — vLLM/SGLang on 8 GPUs. Cannot run on Metal today.** Released 2026-08-28 |

### ⚡ Lane C speed is NOT one number — it varies ~8× by model

**Token time scales with *active* params, not total.** Kimi K3 wakes 104 B per token; DeepSeek-V4-Flash
wakes 13 B. That is **8× fewer bytes read per token**. On a Thunderbolt 4 enclosure (~2,900 MB/s):

| Model | Active | Bytes/token @4-bit | Per token | 500-token answer |
|---|---|---|---|---|
| **`DeepSeek-V4-Flash-0731`** | **13 B** | 6.5 GB | **~2.2 s** | **~18 min** |
| **`GLM-5.3-Flash`** | **18 B** | 9 GB | **~3.1 s** | **~26 min** |
| `GLM-5.2` · `GLM-5.3` | ~40 B | 20 GB | ~6.9 s | ~58 min |
| `DeepSeek-V4-Pro-0813` | 49 B | 24.5 GB | ~8.4 s | ~70 min |
| `Hy4-preview` ⚠️ | 49 B | 24.5 GB | ~8.4 s | ~70 min |
| `Qwen3.8-2.4T-A95B` | 95 B | 47.5 GB | ~16.4 s | ~2.3 h |
| `Kimi-K3` | 104 B | 52 GB | ~17.9 s | ~2.5 h |

*Estimates scaled from the measured internal figure, assuming disk-bound streaming. Real speeds
should be better — the LRU expert cache avoids re-reading experts that repeat across nearby tokens.*

**The Flash tier is not a "submit and walk away" lane.** `DeepSeek-V4-Flash` answers in ~18 minutes and
scores **79.0% SWE-bench Verified**, only 1.6 points below V4-Pro. **Install the Flash tier first** —
302 GB for both, and they are the two most likely to clear Phase 6's "beat Lane A" exit test. Kimi K3
costs **1,700 GB and ~2.5 hours** per answer; it is the ceiling, not the starting point.

⚠️ **Only Kimi K3 and Qwen3.8-2.4T are true "walk away" jobs.** The rest are coffee-break jobs.

### 🔑 Active params ≠ RAM — and the difference enables speculative decoding

**Active params set how many bytes stream from disk per token. They do NOT set RAM residency.**
Lane A is Gemma 4 26B-A4B with **4 B active** — ~2 GB by that arithmetic — yet it **measured 12.23 GB
peak RSS**. The dense trunk, the LRU expert cache and the KV cache dominate, and none appear in the
active-param figure.

**But the Flash tier is small enough that co-residency is plausible:** `DeepSeek-V4-Flash` (6.5 GB
active) plus `GLM-5.3-Flash` (9 GB) is **15.5 GB**, inside the ~20 GB ceiling.

**That is the precondition for cross-lane speculative decoding** (#1 in *Beyond the plan*) — the
drafter and the verifier must both be resident at once. **The Flash giants being small is what makes
that physically possible on a 24 GB machine.** Same for the critic pass (#10) and ensembles (#12).
⚠️ Unverified — trunk and cache overhead decides it, not the active-param number.

**Four things before any download:**
1. ⏸ **Nothing installs today.** Drive is 1+ month out; this needs 4.9 TB.
2. ✅ **Molmo-72B-0924 removed** — replaced by **Molmo2 8B** in Lane B at 1/9 the size and better scores.
3. ✅ **Qwen3-VL-235B dropped** — released **Sept 2025**, and Qwen3.5's unified vision-language foundation **outperforms Qwen3-VL**. Lane A is multimodal either way. **Frees 118 GB.**
4. ⚠️ **Resolve every unconfirmed HF path first.** At these sizes a wrong path wastes an overnight transfer.

**Every model here is MoE** — that is what makes 4.9 TB run in ~8 GB of RAM. Only ~2–4% wakes per token.

**Lane C subtotal: 8 models · ~9,671 B params (~9.67 T) · ~5,135 GB (~5.14 TB).**

---

# THE TOTAL

| Lane | Models | Params | Disk |
|---|---|---|---|
| A — resident | 1 | **27 B → MoE** | **~17 GB** |
| B — specialists | **14** | ~149 B | ~76 GB |
| C — giants | **7** | ~8,901 B | ~4,750 GB |
| **TOTAL** | **23** | **~9.87 T** | **~5.23 TB** |

**Of the 8 TB drive: ~5.23 TB used, ~2.77 TB free.** Still comfortable.
**Only Lane A belongs on the internal disk** — it streams every request, so it needs the measured 3.44 GB/s. **Lanes B and C go external.** Until the drive arrives, install Lane B selectively. — everything else lives external.

---

# 🔧 WHEN A MODEL IS DENSE — CONVERT IT

**Dense is not a dead end and not a reason to reject a model. Convert it to MoE.**

A dense FFN is *already* sparse in practice — most neurons sit near zero for any given token. Dense→MoE
conversion does not add sparsity, it **exposes the sparsity that was always there** by grouping neurons
into experts and adding a router.

## The technique: **CMoE** *(training-free)*

| | |
|---|---|
| **What it does** | Profiles FFN neuron activation on a calibration set. Consistently-hot neurons become **shared experts** (always active); the rest are **balanced k-means clustered** into **routed experts** |
| **Conversion time** | **under 5 minutes on a single GPU** |
| **Training needed** | **none** for the conversion itself |
| **Siblings** | MoEfication · ToMoE · ExpertWeaver · LLaMA-MoE v2 *(post-training)* |

## ⚠️ The measured cost — read before assuming this is free

| Setting | Perplexity | Speed |
|---|---|---|
| **75% activation, training-free** | **Lossless** | **only 5% faster** — no real RAM win |
| **25% activation, training-free** | Llama-2 7B **5.27 → 7.02** (+33%) · Llama-3 8B **6.14 → 10.16** (+65%) | **1.5× lower latency** |
| **25% activation + 1 hr LoRA** (2,000 samples) | recovers **"over 76%"** of dense downstream accuracy | 1.5× |

**Read that honestly: training-free conversion buys you either quality or sparsity, not both.**
Aggressive sparsity costs real accuracy unless you spend an hour of LoRA — and **that is training**,
which the plan's headline promises not to do.

## Two limits the authors state

1. **Quality depends on the calibration dataset** used for activation profiling.
2. **The training-free router "may not fully capture all nuances of routing decisions"** versus a
   trained one.

## ⚠️ One unknown that blocks it today

**The 5-minute conversion is quoted on "a single GPU" — almost certainly CUDA. Whether CMoE runs on
Apple Silicon / Metal is unverified, and this machine has no NVIDIA hardware.** Resolve this before
planning around it. Conversion may need to be done elsewhere and the result copied over.

## The rule this produces

| Model | Do this |
|---|---|
| **Dense and it fits comfortably** | **Use it as-is.** A fitting dense model is *faster* than a streamed MoE — the vault measured 2.9–7.1 tok/s dense against 5.6–26.5 **s/token** streamed |
| **Dense and it does not fit** | **Convert with CMoE**, then decide: 75% activation for quality, 25% for sparsity, or 1 hr LoRA to get closer to both |
| **Already MoE** | Nothing to do — stream the experts |

**Correction to an earlier version of this file:** it said *"no dense model may be Lane A"* and treated
dense as disqualifying. **That was too strong.** Dense is a *convertible* state, not a defect. The real
question is whether the model fits, and if not, whether the conversion's quality cost is acceptable.


---

# 🔴 VERSION AUDIT — apply "latest versions only" to EVERY family

**The rule is family-agnostic: best model per skill by benchmark, newest version of whichever family
wins.** Not "use Qwen." Qwen wins several leaves; it does not win all of them.

**I could not re-verify every family this session — the search budget ran out.** Rather than guess,
here is exactly what is confirmed current and what was replaced. **As of 2026-09-06 nothing is unchecked.**

## ✅ Confirmed current

| Model | Released | Note |
|---|---|---|
| `Qwen3.8-Flash-Next` | **2026-08-26** | Newest Qwen 3.8 open model |
| `Qwen3.8-2.4T-A95B` | 2026-08-12 | |
| `GLM-5.3` | **2026-08-28** | ⚠️ **Newer than GLM-5.2**, but custom licence vs 5.2's MIT. Both kept deliberately |
| `GLM-5.3-Flash` | 2026-08-26 | |
| **`Hy4-preview`** | **2026-08-28** | ⚠️ **Preview.** Apache-2.0, 770B/49B active. **Blocked on Metal — no GGUF/MLX** |
| `Kimi K3` | 2026-07-27 | |
| `GLM-5.2` | 2026-06-13 | Kept for its **MIT licence** and best-in-class math, despite 5.3 existing |

## 🔴 Known stale — DO NOT INSTALL BEFORE REPLACING

| Model | Age | Problem |
|---|---|---|
| ~~`allenai/Molmo-72B-0924`~~ | ✅ **RESOLVED 2026-09-06** | Replaced by **Molmo2 8B** — 1/9 the size, and **beats Gemini 3 Pro on video pointing (38.4 vs 20.0 F1)**. Moved from Lane C to Lane B, freeing **36 GB** |
| `meta-llama/Llama-Guard-3-8B` | 2024 | **Llama Guard 4** exists (April 2025, multimodal). **Not used by Orbi** — Granite Guardian leads on prompt injection, which is the need here |
| **`allenai/wildguard`** | 2024 | Same vintage as Molmo |
| ~~`ibm-granite/granite-guardian-3.x-8b`~~ | ✅ **RESOLVED 2026-09-06** | **Granite Guardian 4.1 8B** (April 2026) confirmed real, adds Bring-Your-Own-Criteria. Ollama: `granite4.1-guardian`. Same size, so no budget change |
| **`BAAI/bge-m3`** | 2024 | Listed as "the production standard" — that was true in 2024 |

✅ **Both stale models that were actually in the lane tables are now resolved** (2026-09-06):
`granite-guardian` → **4.1**, and `Molmo-72B` → **Molmo2 8B**. The remaining three
(`Llama-Guard-3`, `wildguard`, `bge-m3`) are **not used by Orbi** — they exist only in sample 3's wider
registry, and better picks already occupy those roles.

## ❓ Unchecked this session

**✅ Checked and current (2026-09-06):** `nvidia/canary-qwen-2.5b` — still the most accurate open ASR
at **5.63% WER** · `PaddleOCR-VL-1.6` — **28 May 2026**, version now pinned ·
`DeepSeek-V4-Pro-0813` — **GA 13 Aug 2026** · `DeepSeek-V4-Flash-0731` — **31 Jul 2026** ·
`Qwen3-Omni-30B-A3B` — **Qwen3.5-Omni exists but is proprietary**, so this remains the latest *open*
Omni.

**⚠️ Newer versions found — decide at Phase 5:** **Wan 3.0** (public beta 6 Aug 2026, native 30-second
1080p with audio) supersedes Wan 2.7 · **Hunyuan3D v3** (and v2.5) supersede 2.1.

**✅ Second pass complete (2026-09-06) — all remaining models checked:**
`Qwen3-ASR-1.7B` **Jan 2026** · `Qwen3-TTS-12Hz-1.7B` **22 Jan 2026** ·
~~`Qwen3-Embedding-8B`~~ — **#1 on the older MTEB at 70.6, but superseded by Harrier on MTEB-v2** ·
`MiLMMT-46-12B` **Feb 2026**, Gemma3-based, path resolved to `xiaomi-research/`.

**Three upgrades applied:** `Qwen-Image` → **`Qwen-Image-2512`** (weights shipped, Apache-2.0) ·
`Qwen3-Reranker-8B` → **`-4B`** (**beats the 8B on MTEB-R, 69.76**, at half the size) ·
embeddings switched to **`Harrier-oss-v1-27B`** — a three-model family (270M / 0.6B / 27B), MIT,
30 Mar 2026, **#1 on multilingual MTEB-v2**. It replaces `Qwen3-Embedding-8B` outright.

**✅ Audit complete — nothing unchecked.** `Qwen3-VL-235B` was the last one and is **dropped**:
released **23 Sept 2025**, and **Qwen3.5's unified vision-language foundation outperforms Qwen3-VL
models** across reasoning, coding, agents and visual understanding. Both Lane A candidates are
multimodal, so it earned none of its 118 GB.

**On the Qwen3 specialists:** Qwen 3.8 shipped **only three models** — 27B, Flash-Next, 2.4T-A95B.
There is **no Qwen3.8 Omni, VL, Coder, embedding or ASR**, so those roles correctly keep their latest
3.x versions. Re-check on every Qwen release.

**Also unresolved:** `Qwen-Image` vs **`Qwen-Image-2512`** — the 2512 version is newer but its weights
were unpublished at research time. Check before installing.

## The standing job

**This audit is Phase 8's real work, and it starts before Phase 3.** Every row above needs its model
card opened and its release date checked. **Research in this vault ages in weeks** — Qwen shipped
three generations in six months.


---

# WHAT IS NOT VERIFIED

**Read this before downloading anything.**

1. **11 of 23 HF paths are marked ⚠ unconfirmed** in the source research. **Resolve every path before
   Phase 6 downloads 4.9 TB.** A wrong path is a wasted overnight transfer.
2. **Wan 2.7's official weights are on ModelScope, not Hugging Face.** HF copies are community
   re-uploads. Do not treat them as canonical.
3. **Licences are not uniform.** `NLLB` is CC-BY-NC (**excluded** for that reason), `FLUX.2 dev` is
   non-commercial and its params are unpublished (**excluded**), Kimi K3 and GLM-5.3 carry custom
   terms. **Picked on evidence as instructed, licence flagged per row** — an eventual open-source Orbi
   will need to swap the custom-licence rows.
4. **Qwen 3.8 has only three open models** — 27B, Flash-Next, 2.4T-A95B. There is **no Qwen3.8 Omni,
   VL, Coder or embedding variant**, so those roles keep their latest 3.x models. Re-check on each
   Qwen release.
5. **Granite 4.1's Apache-2.0 licence is marked ⚠** — check the model card before install.
   Its **8B tool-calling lead is from a September 2026 roundup, not a single named benchmark**;
   Phase 1's four gates are what actually decide it.
5. **Every 4-bit size is a calculation, not a download.** Real files vary with quant method and
   whether embeddings stay at higher precision. Expect **±10%**.

---

## Change Log

- **2026-09-05 (v1)** — Created as the Phase 2 deliverable the plan called for. Replaces the soft
  "~26 models, ~9.5 T, ~4.9 TB" with an explicit 23-model list whose params and disk actually sum:
  **~9.3 T across ~5.0 TB.** Lane A left deliberately undecided as a **ranked shortlist of three**
  with a four-part measurement test, because no available evidence settles it without running on the
  real machine. **Gemma 4 26B-A4B was considered and rejected with reason** — Turbo Fieldfare runs it
  in ~2 GB at 25–36 tok/s on M4 Pro, but it is weak at Lane A's actual job (Qwen3.6-35B-A3B doubles it
  on MCP tool use, and it loses to Qwen3.8-27B on every compared benchmark). Recorded the **RAM
  ceiling risk**: Lane A at 8 GB plus Qwen3-Omni at 15 GB is 23 GB on a 24 GB machine, so the ASR+TTS
  pair (2.0 GB) is the default voice path instead. Flagged that **11 of 23 HF paths are unconfirmed**
  and must be resolved before any large download.

- **2026-09-05 (v2)** — **Lane A decided: Granite 4.1 8B** (~4.3 GB at 4-bit). Granite 4.1 8B and
  Qwen3.5-9B trade the top spot among open models under 10B as of September 2026; Granite leads on
  **tool calling and coding**, which is Lane A's actual job — routing and emitting valid calls, where
  reliability beats raw score. Qwen3.5-9B is the runner-up on stronger general reasoning, Gemma 4 12B
  third. **Corrected a real error in v1:** it listed "Qwen3-8B (or the current Qwen3.8 8B-class
  release)" — **there is no Qwen3.8 8B.** Qwen3.8 is the 2.4T-flagship generation and its smallest
  open member is **Qwen3.8-27B at ~17 GB**, over 3× the Lane A budget; Qwen3-8B is a separate,
  older-generation model. Both are now listed under Rejected with the distinction spelled out.
  Mach-1 Additive demoted to last resort — its vendor claims remain untested.

- **2026-09-05 (v3)** — **Two corrections on user instruction, both mine.**
  **(1) The standing rule "latest model versions only" was being broken.** v2 carried **Qwen3.5-9B**,
  **Qwen3-8B** and **Qwen3.6-35B** (as Mach-1's base) — three stale Qwen generations. All removed.
  Verified the real Qwen 3.8 open lineup: exactly **three** models — **Qwen3.8-27B** (Apache-2.0,
  native vision, 262K ctx, 2026-08-14), **Qwen3.8-Flash-Next** (180B/6B active, 2026-08-26) and
  **Qwen3.8-2.4T-A95B** (custom licence, 2026-08-12) — plus API-only Qwen3.8-Max. **No Qwen3.8 Omni,
  VL, Coder or embedding exists**, so those Lane B roles correctly keep their latest 3.x models, now
  stated explicitly rather than left ambiguous.
  **(2) The ~5 GB / 8B Lane A cap was my invention, not a requirement.** It existed only so a Lane B
  specialist could sit in RAM beside Lane A, and it silently discarded better models. **Removed.**
  Lane A is now **Qwen3.8-27B at ~17 GB**, the best Qwen 3.8 that runs on this machine, which also
  brings a **native vision encoder** into the router for free. The honest consequence is recorded:
  **Lane A and Lane B now swap rather than co-reside**, costing seconds per switch and buying a far
  better router. Granite 4.1 8B demoted from pick to alternate for RAM-contended cases and background
  subagents. **Qwen3.8-Flash-Next added to Lane C** (90 GB). Totals updated to **24 models · ~9.5 T ·
  ~5.1 TB**, and the vision overlap flagged — Lane A's native vision may make `Qwen3-VL-235B`'s
  118 GB redundant, to be re-tested in Phase 6.

- **2026-09-05 (v4)** — **Three corrections on user instruction, all mine, all substantive.**
  **(1) Lane A was dense — the one shape this machine cannot afford.** v3 picked **Qwen3.8-27B**, a
  **dense** model that fires all 27B every token, contradicting the plan's own premise that sparsity is
  what makes a 9.5 T library fit 24 GB. Replaced with **Qwen3.8-Flash-Next — MoE, 180B total, 6B active
  (3.3%)**, ~90 GB on disk and ~3 GB of active weights. **A rule is now stated at the top of the
  section: no dense model may be Lane A.** The honest risk is recorded too — **no general MoE
  expert-streaming runtime exists for Apple Silicon** (the two that exist are pinned to Kimi K3 and
  Gemma 4 respectively, and MLX does none), so Lane A must stream via `llama.cpp -lm mmap`, and **no
  tok/s figure has ever been published for a 180B/6B MoE on an M4.** Phase 1 measures it first, with
  Gemma 4 26B-A4B and then Granite 4.1 8B as ordered fallbacks.
  **(2) The ~5 GB / 8B Lane A cap is gone.** It was invented so a Lane B model could co-reside, and it
  discarded better models. **Total params are nearly free — active params are the cost.**
  **(3) The file was built around Qwen.** The rule is **best model per skill by benchmark, newest
  version of whichever family wins** — not "use Qwen". A **version audit across every family** was
  added, which immediately found **five known-stale models**, four of them in the guard and embedding
  roles Phase 3 security depends on: **Molmo-72B-0924 (September 2024, two years old)**,
  **Llama-Guard-3**, **WildGuard**, **Granite Guardian 3.x** (Granite is on 4.1) and **BGE-M3**. All
  are flagged do-not-install-before-replacing. Fourteen more models are listed as **unchecked this
  session**, honestly, because the search budget ran out. Totals now **23 models · ~9.5 T · ~5.1 TB**,
  and a new warning records that Lane A (90 GB) plus Lane B (65 GB) is **155 GB against 133 GB free**
  on the internal disk — Lane B must be installed selectively until the external drive arrives.

- **2026-09-05 (v5)** — **Corrected an over-strong rule, on user instruction.** v4 said *"no dense model
  may be Lane A"* and treated dense as disqualifying. **Wrong: a dense model should be converted to
  MoE, not rejected** — a decision this project had already made earlier and I had lost track of.
  Added a section on **CMoE**, which converts a dense LLM to MoE **training-free in under five minutes**
  by profiling FFN activations, making hot neurons shared experts and k-means clustering the rest into
  routed experts (siblings: MoEfication, ToMoE, ExpertWeaver, LLaMA-MoE v2).
  **Recorded the measured cost rather than presenting it as free:** at **75% activation it is lossless
  but only 5% faster**; at **25% activation training-free, perplexity rises sharply** — Llama-2 7B
  5.27→7.02 (+33%), Llama-3 8B 6.14→10.16 (+65%) — and **one hour of LoRA on 2,000 samples recovers
  "over 76%"** of dense accuracy at 1.5× lower latency. Also recorded the authors' two stated limits
  (calibration-set dependence, training-free router imprecision) and **one blocking unknown: the
  conversion is quoted on "a single GPU", almost certainly CUDA, and whether CMoE runs on Metal is
  unverified** — this machine has no NVIDIA hardware, so conversion may have to happen elsewhere.

- **2026-09-06 (v6)** — All three lane tables rewritten to one consistent shape: **grouped by job,
  with a stale flag and a licence column on every row.** Lane A became a single **four-candidate**
  table after the user pointed out a contradiction — the file said *"dense is convertible, not
  disqualified"* and then **rejected Qwen3.8-27B for being dense**. Corrected: **Qwen3.8-27B + CMoE is
  now candidate #1**, since at ~17 GB it fits the real 89 GB free while native-MoE Qwen3.8-Flash-Next
  at 90 GB misses by 1 GB. Two entries were mislabelled "rejected" and are not — Qwen3.8-2.4T-A95B is
  simply **Lane C**, and only Qwen3.8-Max (API-only) and the three stale Qwen generations are genuinely
  out. Lane B and Lane C now surface their **stale models in the table itself** rather than only in the
  audit section: `granite-guardian-3.x` (Granite is on 4.1, and it is Phase 3's guard) and
  `Molmo-72B-0924` (September 2024).

- **2026-09-06 (v7)** — **Version audit continued: five more corrections.** `PaddleOCR-VL` pinned to
  **1.6** (28 May 2026); `DeepSeek-V4-Pro` → **`-0813`** (GA 13 Aug 2026) and `DeepSeek-V4-Flash` →
  **`-0731`** (31 Jul 2026); **Wan 2.7 superseded by Wan 3.0** (public beta 6 Aug 2026 — native
  30-second 1080p with audio, but beta, so 2.7 is kept as the stable fallback); **Hunyuan3D-2.1
  superseded by v3**. **Confirmed current:** `canary-qwen-2.5b` (still the most accurate open ASR at
  5.63% WER) and `Qwen3-Omni-30B-A3B` — **Qwen3.5-Omni exists but is proprietary**, so the Qwen3 Omni
  remains the latest open one. Also noted that **Qwen3.8-Flash-Next is multimodal**, which strengthens
  it as a Lane A candidate, and that **there is no Qwen 4**. **Seven models remain unchecked.**

- **2026-09-06 (v8)** — **Version audit finished.** All seven remaining models checked.
  **Confirmed current:** `Qwen3-ASR-1.7B` (Jan 2026), `Qwen3-TTS-12Hz-1.7B` (22 Jan 2026),
  `Qwen3-Embedding-8B` (still #1 MTEB at 70.6), `MiLMMT-46-12B` (Feb 2026, Gemma3-based, path resolved
  to `xiaomi-research/`). **Three upgrades applied:** `Qwen-Image` → **`Qwen-Image-2512`**, whose
  weights have now shipped under Apache-2.0; `Qwen3-Reranker-8B` → **`-4B`**, because **the 4B beats
  the 8B on MTEB-R (69.76)** and is half the size, the 8B leading only on Chinese; and **Harrier**
  documented properly as a **three-model family (270M / 0.6B / 27B), MIT, 30 March 2026, ranking #1 on
  multilingual MTEB-v2** — **its 27B may beat `Qwen3-Embedding-8B`, so both get benched at Phase 1**.
  Lane B drops to **~130 B / ~67 GB** on the reranker swap. Only `Qwen3-VL-235B` remains unchecked,
  and it is Lane C, drive-gated, and possibly redundant against Lane A's native vision.

- **2026-09-06 (v9)** — **Two deferred decisions made rather than left open.**
  **(1) `Qwen3-VL-235B` dropped from Lane C.** It was released **23 Sept 2025** — a year old — and
  **Qwen3.5's unified vision-language foundation outperforms Qwen3-VL models** across reasoning,
  coding, agents and visual understanding. Both Lane A candidates are already multimodal, so it earned
  none of its **118 GB**. Lane C falls to **7 models · ~8.9 T · ~4,750 GB**.
  **(2) Embeddings switched to `microsoft/Harrier-oss-v1-27B`**, replacing `Qwen3-Embedding-8B`.
  Harrier ranks **#1 on multilingual MTEB-v2** — the newer benchmark — is **MIT**, ships 30 Mar 2026,
  and its 0.6B already beats Qwen3-Embedding-0.6B (nDCG@3 0.8911 vs 0.8168). Qwen3-Embedding-8B leads
  only the older MTEB. **Cost: 13.5 GB against 4.3 GB**, so `Harrier-0.6B` stays as the fast path for
  when that is too heavy. Chosen on benchmark evidence, per the standing rule.
  **Totals now 22 models · ~9.1 T · ~4.84 TB. Nothing in the list is unchecked.**

- **2026-09-20 (v10)** — **Corrected a flat figure that was wrong by up to 8×.** Lane C carried
  *"~25 s/token"* for all seven giants; that is **Kimi K3's** number applied to models that differ
  enormously. **Token time scales with *active* params, not total**, so `DeepSeek-V4-Flash` at 13 B
  active reads **8× fewer bytes per token** than Kimi K3 at 104 B. Real range on a Thunderbolt 4
  enclosure is **~2.2 s/token (≈18 min for 500 tokens) up to ~17.9 s/token (≈2.5 h)**. **Only Kimi K3
  and Qwen3.8-2.4T are genuinely "submit and walk away"** — the Flash tier is a coffee break, and
  `DeepSeek-V4-Flash` scores **79.0% SWE-bench Verified**, 1.6 points off V4-Pro, for 142 GB instead of
  1,700. Install order changed to Flash-tier first, Kimi K3 last; **Kimi K3 remains in the plan** at
  user instruction as the most capable model.
  Also recorded a distinction the file had been eliding: **active params are not RAM residency.** Lane A
  has 4 B active (~2 GB) but **measured 12.23 GB peak RSS** — trunk, expert cache and KV cache dominate.
  The consequence is positive: the Flash tier's active sets total **15.5 GB**, inside the ~20 GB
  ceiling, so **two giants may co-reside — which is the precondition for cross-lane speculative
  decoding** (#1), the critic pass (#10) and ensembles (#12). Flagged as unverified: overhead decides
  it, not the active-param arithmetic.
- **2026-10-30 (plan v54)** — Reward machine is now the Kildall server (MI210 64 GB HBM2e + 512 GB DDR4 on 8 channels + 8 TB NVMe). Row 7b: DeepSeek-V4.1-Flash (~380 GB at 4-bit) now fits that server's RAM + VRAM as a resident candidate, speed unmeasured; its NIM status corrected with slice 5c (timed out once, not qualified). No model added or removed.
