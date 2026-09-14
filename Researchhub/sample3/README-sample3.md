# Sample 3 — what changed, and why it exists

**Created:** 2026-09-02. **Forked from sample 2** after a careful read of `sample 1/OrbiLLM`.

**The question asked:** does anything in `sample 1/OrbiLLM` improve sample 2?
**The answer: yes** — enough to justify a fork, and one item **corrects a false claim** sample 2 was
making.

Sample 2 is **not wrong and not superseded wholesale**. Sample 3 is sample 2 **plus** the prior Orbi
research that sample 2 never incorporated. Everything else is byte-identical.

---

## Why sample 1 had anything to offer

Sample 2 was built from scratch, deliberately ignoring the rest of the vault, because that is what was
asked. That was the right call for independence — and it meant **prior research on this exact machine
was never consulted.**

`sample 1/OrbiLLM/Hardware/` contains two documents written against a **Mac mini M4, 24 GB** — the
same target as `UHWmini.md`:

| File | Lines | What it had |
|---|---|---|
| `3.5T local LLM hardware workflow.md` | 172 | Deep research into 8 named tools **on this exact machine** |
| `hwmini.md` | 353 | Combined hardware-minimisation guide, incl. sparse upcycling |

It also holds a **full local clone of the Soup repository** (`LLMtrain/Soup/`) with its `docs/` and
`benchmarks/` — primary source material that `LLM train/Soup-finetune&train.md` was written *without*,
since that file was built from the GitHub README alone.

---

## The five changes, all in `UHWmini.md`

### 1. ✅ "Turbo Fieldfare" — resolved

Sample 2 flagged this as unfindable and **refused to invent an entry** — the right call at the time.
Sample 1 had it. **Verified live 2026-09-02:**

**[`drumih/turbo-fieldfare`](https://github.com/drumih/turbo-fieldfare)** — Apache-2.0, **6,535 stars,
410 forks**, **Swift**, first commit 2026-07-17, pushed 2026-08-29.
*"Gemma 4 26B-A4B inference in **~2 GB of RAM** on any M-series MacBook."*

Native **Swift + Metal**, streaming routed experts from a custom `.gturbo` format through a
**16-slot-per-layer LFU cache**. **4–6 tok/s on M1/M2 Air, 25–36 tok/s on M4 Pro/M5.**
**Hard-pinned to one model and one quantisation** by design.

### 2. ⚠️ A false claim, corrected

Sample 2's §7 said **MoE expert streaming from SSD does not exist on Apple Silicon**, citing the open
mlx-lm feature request.

**That is true of MLX and false in general.** Turbo Fieldfare does it today, natively. §7 now says so,
and records that **two** macOS/arm64 projects do it — Turbo Fieldfare and `kimi-k3-in-c` — not one.

### 3. SGLang + MLX + RadixAttention — the biggest practical addition

An **official Apple Silicon path** via `SGLANG_USE_MLX=1` (confirmed: **19 code hits** in
`sgl-project/sglang`), measured at **3.9–4.6× the naive Mac backend**, shipping **RadixAttention** —
radix-tree KV reuse that lets requests sharing a prompt prefix **skip recomputing it entirely**.

**That is exactly the agentic-coding pattern** in §4: a fixed system prompt plus tool definitions,
re-sent every turn. Now #10 on the action list.

### 4. Two tools and a build-time lever added

- **AirLLM** — layer-by-layer streaming; a **70B dense model to ~1.6 GB active, without quantisation**
- **Turbovec** — Rust vector index, **31 GB → 4 GB (16×)**, hand-written **NEON** kernels, within
  **2–25% of FAISS on ARM**
- **§6b Sparse upcycling** — dense→MoE conversion (Komatsuzaki et al., Google 2022 / ICLR 2023), the
  only **build-time** lever in the document, with the caveat that it needs training compute *and* a
  streaming engine — two unbuilt steps

### 5. ⚠️ A KIVI correction

KIVI's widely-quoted **2.6× memory / 2.35–3.47× throughput** figures trace to **an arXiv ID that does
not match KIVI's actual publication**, and were **refuted in adversarial verification** during the
earlier research. **The mechanism is real; those numbers are not.** Do not quote them.

---

## What did NOT change

Every other file is **identical to sample 2**. Sample 1's other OrbiLLM documents were read and
judged **superseded rather than additive** — sample 2's versions are newer, longer and better sourced:

| Sample 1 | Sample 2 equivalent | Verdict |
|---|---|---|
| `Orbi OSSLLM research.md` (548 lines) | `OrbiOSS.md` (2,533 lines, 1,074 leaves) | superseded |
| `Hardware/kimi k3 hw mini.md` (80) | `kimik3 hwmini.md` (173) | superseded |
| `Hardware/qwen 3.8 hw mini.md` (78) | `qwen38-27b hwmini.md` (181) | superseded |
| `Hardware/mach 1 hw mini.md` (65) | `mach1 hwmini.md` (180) | superseded |
| `text humanize.md` (98) | `texthuman.md` (244) | superseded |
| `uncencored content.md` (66) | `uncensoredcontent.md` (261) | superseded |
| `cloud call.md` (147) | `Cloudcall/` (22 files) | superseded |
| `LLMtrain/LLM-autotrain.md` (104) | `LLM train/LLM-autotrain.md` (579) | superseded |

---

## Known remaining gap — the largest one

**The local Soup clone at `sample 1/OrbiLLM/LLMtrain/Soup/` was NOT mined**, and it should be.

`LLM train/Soup-finetune&train.md` states in its own gaps section that it is *"README-level reading
only"* and that *"the benchmark records under `benchmarks/` were not opened."* **Those files are
sitting on disk locally:**

| File | Lines | Why it matters |
|---|---|---|
| `benchmarks/gate-h100-validation.md` | **5,017** | the H100 comparison cited secondhand |
| `benchmarks/probe-v0.73.0-what-bounds-streaming.md` | — | **the streaming-bound analysis quoted secondhand** |
| `benchmarks/gate-v0.73.1-measured-vram-fit.md` | — | **measured VRAM fit** |
| `docs/performance-and-quantization.md` | 816 | directly relevant to `UHWmini.md` |
| `docs/peft-and-efficiency.md` | 592 | |
| `CHANGELOG.md` | 3,274 | |

**Reading them would let the Soup file's figures be upgraded from secondhand to primary**, and would
likely add material to `UHWmini.md`. It was scoped out of this pass for cost, not because it lacks
value. **This is the highest-value remaining work in the vault.**

## Change Log

- **2026-09-02** — Created sample 3 as a fork of sample 2, after reading `sample 1/OrbiLLM` on request.
  Concluded **yes, sample 1 improves sample 2**, and made five changes, all confined to `UHWmini.md`
  (665 → **781 lines**, 42 → **47 sources**): resolved **Turbo Fieldfare** as the real, live
  `drumih/turbo-fieldfare` (Apache-2.0, 6,535★, Swift, Gemma 4 26B-A4B in ~2 GB, pinned to one model);
  **corrected sample 2's false claim** that Apple Silicon MoE expert streaming does not exist, which is
  true only of MLX; added **SGLang + MLX (`SGLANG_USE_MLX=1`, 3.9–4.6×) with RadixAttention** as the
  strongest serving upgrade for agentic sessions; added **AirLLM**, **Turbovec** and a
  **sparse-upcycling** section; and recorded a **KIVI correction** where the commonly-quoted figures
  trace to a mismatched arXiv ID and were refuted in earlier adversarial verification.
  Judged sample 1's other eight OrbiLLM documents **superseded** by sample 2's longer, newer versions
  and left them out. Recorded the **largest remaining gap**: the local Soup repository clone at
  `sample 1/OrbiLLM/LLMtrain/Soup/` — with 5,017 lines of H100 validation, the streaming-bound probe,
  a measured-VRAM-fit gate, and 816 lines of performance-and-quantization docs — **was not mined**, and
  doing so would upgrade `Soup-finetune&train.md` from secondhand to primary sourcing.
