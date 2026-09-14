# qwen38-27b hwmini — Qwen3.8-27B Hardware Minimisation & Pace Architecture

**Source:** [ofox.ai — Qwen 3.8 27B run locally, VRAM & GGUF, 2026](https://ofox.ai/blog/qwen-3-8-27b-run-locally-vram-gguf-2026/)
**Built:** 2026-09-01 · Sample 2 · self-contained

**One line:** a *dense* 27B model whose memory savings come almost entirely from **quantisation**,
plus an architectural trick that cuts the KV cache to **a quarter** of a conventional model's.

---

## 1. What the model is

| Field | Value |
|---|---|
| Name | **Qwen3.8-27B** (27.32B as counted by llama.cpp) |
| Architecture | **Dense** transformer with **hybrid attention** |
| Attention split | **16 of 64 layers full attention; 48 layers Gated DeltaNet linear attention** |
| Native context | **262,144** tokens (1M via YaRN) |
| Licence | **Apache-2.0**, commercial use allowed |
| Vision | optional projector, +0.63–0.93 GB |

**Dense matters.** Every parameter is active on every token. There is no sparsity to exploit, so
none of the expert-streaming tricks that make a 2.78T MoE fit in 8 GB (see `kimik3 hwmini.md`) apply
here. **Quantisation and offload are the only levers.** That is the single most important structural
fact about this model's hardware story.

---

## 2. Hardware-minimisation architecture

### 2.1 Lever one — quantisation (the main lever)

| Precision | Guidance (RAM+VRAM) | Actual GGUF size |
|---|---|---|
| 2-bit | 11–13 GB | **9.01–10.68 GB** |
| 3-bit | 13–16 GB | 11.91–13.82 GB |
| 4-bit | 17–19 GB | 16.06–17.92 GB |
| 6-bit | 24 GB | 22.43–25.92 GB |
| 8-bit | 31 GB | 28.60–31.46 GB |
| BF16 | 56 GB | **53.81 GB** |

**The figure people misread**, quoted from the source: *"The 17 GB figure… is RAM plus VRAM, or
unified memory… not 17 GB sitting in VRAM."* Budget total addressable memory, not card capacity.

**Publishers differ materially at the same nominal quant:**

| Publisher | Q4_K_M | Full range | Note |
|---|---|---|---|
| lmstudio-community | **16.81 GB** | 16.81–29.05 GB | smallest 4-bit |
| Unsloth | 17.11 GB | 9.01–31.46 GB | 21 variants; `UD` prefix = dynamic quants |
| ggml-org | 18.97 GB | 18.97–53.81 GB | separate MTP weights available |

Two GB of spread on the *same* quant level. On a 16 GB machine that is the difference between
running and not running.

### 2.2 Lever two — the KV cache, and the architectural win

This is where the hybrid attention pays off. KV cache at f16:

| Context | Cache | Total with 3-bit UD-Q3_K_XL |
|---|---|---|
| 8,192 | 0.5 GB | 13.0 GB |
| 32,768 | 2 GB | 14.5 GB |
| 131,072 | 8 GB | 20.5 GB |
| 262,144 | **16 GB** | 28.5 GB |

**A conventional 64-layer model needs four times this cache.** Only 16 of 64 layers run full
attention; the other 48 use Gated DeltaNet linear attention, which does not grow a per-token KV
entry the same way. **That is a real architectural memory saving, not a quantisation trick** — and
it is the only one this model has.

Further halving is available by quantising the cache itself:

```bash
--cache-type-k q8_0 --cache-type-v q8_0    # ~50% cache reduction
```

Note the shape of the numbers: at 256K context the **cache (16 GB) is roughly as large as the
weights** at 3-bit. Past ~100K context, context is the dominant cost, not the model.

### 2.3 Lever three — offload (pay in speed)

For a 16 GB card the choice is explicit: **3-bit entirely on GPU (13.44 GB)**, or **4-bit with RAM
offload**. The source's verdict: it *"works either way. Offload costs speed"* — generation drops to
DDR bandwidth.

---

## 3. Pace architecture — measured, not claimed

**M2 Pro, 16 GB unified, llama.cpp b10450:**

| Quant | Prompt (pp512) | Generation (tg128) | Real 7,072-token prompt |
|---|---|---|---|
| UD-IQ2_XXS (2-bit) | 74.59 tok/s | **7.11 tok/s** | 33.84 tok/s prompt / **2.91 tok/s gen** |
| Q4_K_M (4-bit) | 18.84 tok/s | **fatal error (-3)** | paging failure |

Two things worth staring at:

1. **Synthetic 7.11 tok/s becomes 2.91 tok/s on a real 7K prompt** — a **2.4× drop**. Benchmark
   numbers taken at tiny context do not survive contact with real prompts.
2. **4-bit does not merely run slowly on 16 GB — it dies.** `failed to decode generation batch,
   res = -3`. The failure mode is a crash, not graceful degradation.

Reference point: an RTX 4090 reportedly hits **25.57 tok/s** generation on a 4-bit Qwen 3.6 of the
same file size — roughly **3.6× the M2 Pro's synthetic 2-bit figure**, on a model it can hold
entirely in VRAM.

### The thinking-budget trap

`reasoning_effort: xhigh` **consumes the `max_tokens` budget before producing an answer.** On a
machine already generating at single-digit tokens/sec, a high thinking budget is the difference
between a slow answer and no answer. Set `reasoning_effort: low` for routine work.

---

## 4. Practical configuration

| Hardware | Best quant | Context |
|---|---|---|
| RTX 5090 (32 GB) | 4-bit or 6-bit | 32K viable |
| RTX 4090 (24 GB) | 4-bit | vendor-recommended |
| RTX 5080 / 5070 Ti (16 GB) | 3-bit on GPU **or** 4-bit + offload | compromises required |
| Mac 32 GB+ unified | 4-bit | ~75% of RAM usable |
| Mac 16 GB unified | **2-bit only** | Metal ceiling **12.71 GB** |

**Quant picks:** 32 GB+ → `UD-Q4_K_XL` (17.92 GB) or `Q6_K` (22.88 GB) · 24 GB → `Q4_K_M`
lmstudio-community (16.81 GB) · 16 GB → `UD-Q3_K_XL` (13.44 GB) · 16 GB Mac → `UD-IQ2_XXS`
(9.01 GB), described as *"the floor, with noticeable quality loss."*

```bash
brew install llama.cpp

llama-server -m qwen38-27b.gguf -c 16384 --temp 1.0 --top-p 0.95 --top-k 20 --port 8080
llama-server -m qwen38-27b.gguf --mmproj mmproj.gguf -c 16384 --port 8080      # vision
llama-server -m qwen38-27b.gguf --cache-type-k q8_0 --cache-type-v q8_0 -c 16384
```

### Failure table

| Symptom | Cause | Fix |
|---|---|---|
| `failed to decode generation batch, res = -3` | weights exceed working set | drop one quant level |
| 3–4× slower than benchmarks | file larger than addressable memory | check `recommendedMaxWorkingSetSize` at startup |
| `modalities: text` on a vision model | projector not loaded | download mmproj, pass `--mmproj` |
| endless repetition (non-thinking) | missing presence penalty | `--presence-penalty 1.5` |

**Source's bottom line, quoted:** *"A 24 GB card is the entry point for the quant Qwen actually
wants you to use, and 32 GB is where it stops being a squeeze."*

---

## 5. Honest gaps

- **Single-source file.** Everything above comes from one blog post. Only the model's Apache-2.0
  licence and general availability were cross-checked. The benchmark numbers were **not**
  independently reproduced.
- **One machine, one build.** All timings are M2 Pro 16 GB on llama.cpp b10450. The RTX 4090 figure
  is second-hand *and for a different model* (Qwen 3.6), used only as a rough scale reference.
- **No quality measurement.** "Noticeable quality loss" at 2-bit is the source's wording, with no
  benchmark attached. How much a 2-bit Qwen3.8-27B actually degrades is unmeasured here.
- **Speed can be improved further** by a technique this post does not cover — see
  `dflash2 hwmini.md`, which addresses pace rather than memory.

## Sources

1. [ofox.ai — Qwen 3.8 27B run locally: VRAM, GGUF (2026)](https://ofox.ai/blog/qwen-3-8-27b-run-locally-vram-gguf-2026/) — everything above unless stated
2. [unsloth/Qwen3.8-27B-GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF) — quant variants referenced

## Change Log

- **2026-09-01** — Created from the ofox.ai deployment guide. Headline finding: this is a **dense**
  model, so unlike the MoE cases in this folder its memory story is quantisation-only — with **one**
  genuine architectural saving, the hybrid attention (16 of 64 layers full, 48 Gated DeltaNet) that
  cuts KV cache to **a quarter** of a conventional 64-layer model. Recorded that at 256K context the
  cache (16 GB) roughly equals the weights at 3-bit, so past ~100K context the context dominates
  cost. Two failure realities captured that marketing numbers hide: synthetic 7.11 tok/s falls to
  **2.91 tok/s** on a real 7K-token prompt (2.4× drop), and 4-bit on a 16 GB Mac **crashes** with
  `res = -3` rather than degrading. Also noted a **2 GB spread between publishers at the same
  nominal quant**, which decides whether a 16 GB machine runs at all. Single-source file; benchmarks
  not independently reproduced.
