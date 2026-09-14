# dflash2 hwmini — DFlash 2: Pace Architecture (not a memory technique)

**Source:** [threads.com/@_theorum_/post/DcjJZ6tD4y1](https://www.threads.com/@_theorum_/post/DcjJZ6tD4y1)
**Built:** 2026-09-01 · Sample 2 · self-contained

**One line:** a **block-diffusion drafter** for speculative decoding that makes Qwen3.8-27B generate
2.7–3.4× faster **with byte-identical output** — and whose headline laptop number does not survive
independent testing.

> **This file breaks the folder's pattern deliberately.** The other three `hwmini` files are about
> **fitting** a model into less hardware. DFlash 2 changes **neither** the model nor its memory
> footprint — it changes **how fast tokens come out**. It is pure pace architecture. It is filed here
> because it stacks *on top of* `qwen38-27b hwmini.md`: same model, same weights, same VRAM, more
> speed. It is also the only technique here that **adds** memory rather than saving it.

---

## 1. The claim being checked

The Threads post, in full:

> *"Qwen3.8-27B can now run at around 70 tokens/sec locally on your laptop. And no, they didn't
> replace it with a smaller model or sacrifice quality. The trick is a new decoding method called
> DFlash 2 ↓"*

Three separate claims: **~70 tok/s on a laptop**, **no smaller model**, **no quality loss**. Two hold
up. One does not.

---

## 2. How it works

### 2.1 Standard speculative decoding, for contrast

A small draft model guesses the next few tokens **one at a time**; the big model verifies them all in
a single forward pass. Accepted guesses are free; rejected ones cost a rollback. Output is identical
to the big model's, because the big model is the arbiter.

### 2.2 What DFlash 2 changes

DFlash 2 is a **block-diffusion drafter**. Instead of drafting one token at a time:

1. It predicts an **entire block of tokens in a single pass**.
2. It keeps the **top candidates at every position** in that block — a lattice, not a line.
3. A **lightweight selector traces one coherent path** through those candidates.
4. The target model verifies that path in one forward pass.

```
 autoregressive draft:   t1 → t2 → t3 → t4        (sequential, one pass each)

 DFlash 2 block draft:   ┌ t1a  t2a  t3a  t4a ┐
                         │ t1b  t2b  t3b  t4b │   one pass, top-k per position
                         └ t1c  t2c  t3c  t4c ┘
                              ▼ selector traces one coherent path
                           t1a  t2b  t3a  t4c  → verified by the 27B in one pass
```

The gain is that **drafting stops being sequential.** Classic speculative decoding's drafter is
itself autoregressive and becomes the bottleneck; a block-diffusion drafter removes that serialisation.

### 2.3 It *is* a second model — correcting a common misreading

DFlash 2 pairs the target model with **a small draft model**. It is not a change to Qwen3.8-27B's
own weights or a sampling flag. It ships as its own artefact, alongside the target:

| Repo | What it is |
|---|---|
| [`incoai/Qwen3.8-27B-DFlash2`](https://huggingface.co/incoai/Qwen3.8-27B-DFlash2) | drafter, native weights |
| [`incoai/Qwen3.8-27B-DFlash2-GGUF`](https://huggingface.co/incoai/Qwen3.8-27B-DFlash2-GGUF) | GGUF, for llama.cpp / CPU-focused backends |
| [`z-lab/Qwen3.8-27B-DFlash2`](https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2) | z-lab release |
| [`z-lab/Qwen3.8-27B-DFlash2-GGUF`](https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2-GGUF) | GGUF variant |

**So the memory story is negative, not positive:** you load the 27B *and* a drafter. On the 16 GB
machines in `qwen38-27b hwmini.md` — where 4-bit already crashes with `res = -3` — the extra
resident drafter is a real cost against an already-failing budget.

**Engine support:** SGLang, with support noted for vLLM and llama.cpp. Pick the GGUF builds for
llama.cpp.

---

## 3. Pace — claimed vs measured

| Setting | Hardware | Result |
|---|---|---|
| GSM8K, concurrency 1 | **NVIDIA H200** | **236.1 tok/s — 3.43× speedup** |
| General | H200 | **2.7–3.4×** throughput vs autoregressive |
| **llama.cpp, real test** | **M5 Max MacBook Pro** | **11–35 tok/s** across thinking levels |

### The gap that matters

The Threads post says **~70 tok/s on a laptop.** Direct testing on an **M5 Max MacBook Pro** — a
high-end laptop, not a weak one — produced **11–35 tok/s**, described by the tester as
*"far below the advertised 70 tokens per second."*

**The 236 tok/s figure is real and also irrelevant to the claim**: it is an H200 datacentre GPU at
concurrency 1, not a laptop. The post appears to have carried a datacentre-class speedup into a
laptop sentence.

**What survives:**

| Claim | Verdict |
|---|---|
| "no smaller model" | ✓ **true** — the 27B still produces every token; the drafter only proposes |
| "no quality sacrificed" | ✓ **true** — the target model verifies, so output matches |
| "~70 tok/s on your laptop" | ✗ **not supported** — measured 11–35 tok/s on an M5 Max |

The **speedup ratio** is the honest way to state the benefit — roughly 2–3× on whatever your
hardware already does — not an absolute tokens/sec number.

---

## 4. How it stacks with the rest of this folder

| File | Lever | Changes memory? | Changes quality? | Changes speed? |
|---|---|---|---|---|
| `qwen38-27b hwmini.md` | quantisation + KV-cache architecture | **↓ large** | ↓ real at low bits | ↓ (offload costs speed) |
| `kimik3 hwmini.md` | expert streaming from disk | **↓ extreme** (RAM→disk) | **none** | ↓↓ (s/token) |
| `mach1 hwmini.md` | MoE + 1.7-bit additive + fused kernels | **↓ large** | ↓ ~3.7% | ↑ |
| **`dflash2 hwmini.md`** | **block-diffusion speculative decoding** | **↑ adds a drafter** | **none** | **↑↑ 2.7–3.4×** |

DFlash 2 is the only entry that **buys speed with memory** instead of trading memory for something
else. On a machine with headroom that is an excellent trade. On a 16 GB Mac running 2-bit because
nothing larger fits, it is the wrong tool — you have no memory to spend.

**Stacking order that makes sense:** quantise to fit first, then add DFlash 2 only if memory remains.

---

## 5. Honest gaps

- **No primary source read.** The Inco AI blog and the Hugging Face model cards were identified but
  **not fetched**. Everything here comes from the Threads post plus secondary coverage. The
  block-diffusion mechanism description in particular deserves checking against
  [inco.ai/blog/dflash2](https://inco.ai/blog/dflash2/).
- **Nothing measured.** Neither the 236 tok/s nor the 11–35 tok/s figure was reproduced.
- **Two publishers, unexplained.** `incoai/*` and `z-lab/*` both publish what appears to be the same
  drafter. Which is canonical, and whether they are identical, was not established.
- **Drafter size unknown.** The memory cost of adding it — the crux of whether it is usable on a
  constrained machine — is not quantified anywhere in these sources.
- **"Byte-identical output" is inferred**, not directly measured here. It follows from how
  speculative decoding works (the target model verifies every token), and the sources assert no
  quality change, but no diff test was run.
- **Early-stage.** This is a recent technique; the M5 Max result suggests llama.cpp integration is
  less mature than the SGLang path.

## Sources

1. [threads.com/@_theorum_/post/DcjJZ6tD4y1](https://www.threads.com/@_theorum_/post/DcjJZ6tD4y1) — the ~70 tok/s claim
2. [DFlash 2: Keep Drafting Parallel — Inco AI](https://inco.ai/blog/dflash2/) — first-party; **identified, not fetched**
3. [`incoai/Qwen3.8-27B-DFlash2-GGUF`](https://huggingface.co/incoai/Qwen3.8-27B-DFlash2-GGUF)
4. [`z-lab/Qwen3.8-27B-DFlash2`](https://huggingface.co/z-lab/Qwen3.8-27B-DFlash2)
5. [DFlash 2: Run Qwen3.8-27B at 2x Speed — MindStudio](https://www.mindstudio.ai/blog/dflash-2-speculative-decoding-qwen) — the 236.1 tok/s H200 figure
6. [Qwen3.8-27B: Low vs xHigh Thinking + DFlash2 on M5 Max — daily.dev](https://daily.dev/posts/qwen3-8-27b-low-vs-xhigh-thinking-dflash2-speculative-decoding-on-m5-max--ud8lzf0bl) — the contradicting 11–35 tok/s measurement
7. [Qwen3.8-27B-DFlash2: A Guide to Faster Qwen Inference — HackerNoon](https://hackernoon.com/qwen38-27b-dflash2-a-guide-to-faster-qwen-inference)

## Change Log

- **2026-09-01** — Created from the @_theorum_ Threads post. Filed with the `hwmini` set but
  explicitly **not** a hardware-minimisation technique: DFlash 2 changes neither the model nor its
  footprint, only generation speed, and is the **only** entry in this folder that **adds** memory
  rather than saving it.
  Mechanism recorded: a **block-diffusion drafter** that predicts a whole block of tokens in one
  pass, keeps **top candidates at every position**, and uses a lightweight selector to trace one
  coherent path, which the 27B then verifies in a single forward pass — removing the sequential
  bottleneck that a classic autoregressive drafter creates. Confirmed it **is a separate small draft
  model** shipped as its own artefact (`incoai/*` and `z-lab/*`, native and GGUF), not a flag or a
  weight change — so on the 16 GB machines where 4-bit Qwen3.8-27B already crashes with `res = -3`,
  the extra resident drafter is a real cost.
  **Principal finding: the post's headline number is not supported.** It claims **~70 tok/s on a
  laptop**; direct llama.cpp testing on an **M5 Max MacBook Pro** measured **11–35 tok/s**,
  explicitly *"far below the advertised 70."* The genuine **236.1 tok/s / 3.43× on GSM8K** figure is
  an **H200 datacentre GPU** at concurrency 1 — real, but carried into a laptop sentence where it
  does not belong. The post's other two claims **do** hold: no smaller model is substituted, and
  output quality is unchanged because the target model verifies every token. Concluded that the
  honest way to state the benefit is the **ratio (~2–3× of whatever your hardware already does)**,
  never an absolute tokens/sec figure.
  Added a cross-file stacking table and the resulting rule: **quantise to fit first, add DFlash 2
  only if memory remains** — it is the wrong tool on a machine already at its ceiling.
  Not done: the first-party Inco AI blog and the model cards were identified but not fetched, no
  figure was reproduced, the drafter's own size is unknown, and the two publishers' relationship is
  unexplained.
