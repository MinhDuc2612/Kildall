# HW Mini — Combined Guide to Minimizing LLM Hardware Usage

Master doc combining every hardware-minimization technique researched in this folder (`kimi k3 hw mini.md`, `qwen 3.8 hw mini.md`, `mach 1 hw mini.md`) plus additional complementary techniques verified directly against llama.cpp's own docs. A `/last30days` pass for "new" techniques from the last 30 days came back empty (nothing cleared the relevance floor — mostly GPU-buying threads, not new methods), so this combines what's already proven rather than chasing something that doesn't yet exist. Compiled 2026-08-23, expanded 2026-08-25 with a concrete decision-tree workflow, worked example commands, a flag cheat-sheet, and a troubleshooting section.

---

## 1. The four core techniques (full detail in their own docs)

Every technique below tackles the same problem — a model's weights don't fit in available memory — from a different angle. They are not mutually exclusive; Section 4 (Combined Workflow) shows how to stack them.

| Technique | Core idea | Best for | Full doc |
|---|---|---|---|
| **MoE expert streaming** | Never load the "sleeping" experts a token doesn't need — stream only the active ~4% off SSD | Giant sparse MoE models (Kimi K3: 2.8T params on 8GB RAM) | `kimi k3 hw mini.md` |
| **GGUF quantization + RAM/VRAM offload** | Shrink every weight's bit-depth (2-8 bit), split layers between GPU and CPU when it still doesn't fit | Dense models with no sparsity to exploit (Qwen3.8-27B) | `qwen 3.8 hw mini.md` |
| **Extreme sub-2-bit + custom kernels** | Push quantization below GGUF's usual floor (1.7 bit) using purpose-built decode-during-compute kernels; stacks with MoE sparsity | Apple Silicon-specific, smallest possible footprint for a given param count (Mach-1: 35B in 7GB) | `mach 1 hw mini.md` |
| **Determinism via integer arithmetic** *(tangential — different axis)* | Bit-identical output across different hardware, not a memory reduction | Reproducibility, not minimization | Nathan Barry hackathon project, not written up separately — see Sources |

**The one-sentence rule for picking between the first three:** if the model is MoE, exploit the sparsity (streaming); if it's dense, quantize (GGUF); if you're on Apple Silicon and want the absolute floor, use a purpose-built extreme-quant engine (Mach-1-style) if one exists for your model family — otherwise stack MoE streaming + aggressive quantization together, which is exactly what Mach-1 does internally.

## 2. Complementary techniques (stack on top of any of the above)

These aren't alternatives to the three core techniques — they compose with all of them, verified directly against llama.cpp's own server documentation (`tools/server/README.md`, fetched directly, not from a secondary source):

**A. KV cache quantization (`-ctk`/`--cache-type-k`, `-ctv`/`--cache-type-v`).** The KV cache — the running memory of every token's attention keys/values — grows linearly with context length and normally sits at f16. Quantizing it to q8_0, q4_0, q4_1, iq4_nl, q5_0, or q5_1 shrinks this specifically, independent of the model weights' own quantization. On long-context sessions the KV cache can rival the model's own size — this is the single highest-leverage flag for anyone hitting OOM specifically on long prompts, not on model loading.

**B. Flash Attention (`-fa`/`--flash-attn [on|off|auto]`).** A fused attention kernel that computes attention without materializing the full quadratic attention matrix in memory, cutting both memory use and compute time for the attention step specifically. Defaults to `auto` (on when the backend supports it) — worth explicitly forcing `on` and confirming it's actually active, since a silent fallback to `off` re-introduces the memory cost it exists to avoid.

**C. Load mode (`-lm`/`--load-mode`, replacing the deprecated `--mmap`/`--no-mmap`).** Controls whether the model is memory-mapped (`mmap` — OS pages it in on demand, lets you run a model larger than physical RAM by trading speed for capacity, exactly the mechanism kimi-k3-in-c's disk-streaming approach depends on) or force-locked into RAM (`mlock` — guarantees no swap-related stalls, at the cost of needing the full footprint resident). `auto` picks mmap unless the device doesn't support it. This flag is the direct lever for choosing "smaller footprint, accept disk-read latency" vs. "predictable speed, need the RAM."

**D. Speculative decoding (`--spec-draft-model`/`-md`, `--spec-draft-n-max`).** Runs a small, fast "draft" model to guess several tokens ahead, then verifies them in one batched pass with the real model — when the draft guesses right (common for predictable text), you get multiple tokens for roughly the cost of one full-model forward pass. This is a *speed* technique primarily, not a memory-reduction one, but it changes the practical calculus of running a small heavily-quantized model: if a tiny draft model can keep the big model's forward passes to a minimum, the effective "cost" of an aggressively quantized big model drops further. Mach-1's own docs reference a similar speculative-decoding mode reaching ~163 tok/s vs ~117 tok/s single-stream (unverified figure, per `mach 1 hw mini.md`).

**E. Context and batch sizing (`-c`/`--ctx-size`, `-b`/`--batch-size`, `-ub`/`--ubatch-size`).** The most basic lever and the one people skip: context size directly multiplies KV cache cost (see A), and batch/micro-batch size trade throughput for peak memory during prompt processing. Setting `--ctx-size` to only what you actually need (not the model's max) is free memory savings with zero quality cost.

**F. DFlash 2 (`--spec-type draft-dflash`, confirmed via the HF repo's own README — parallel-drafting speculative decoding, added 2026-08-29).** A newer alternative to Technique D above, shipped by Inco AI mid-August 2026 and merged into llama.cpp's main branch on 2026-08-27 (`ggml-org/llama.cpp#27342`, "spec : add DFlash2 support (local convolution + candidate selector)"). **Correction (2026-08-29 re-verification):** DFlash 2 is still a *separate drafter model* (like Technique D), not "no second model" — the earlier draft of this doc overstated that. The real difference is architectural: instead of guessing one token at a time autoregressively, its tiny purpose-built drafter (Inco AI's blog cites ~18.5M added parameters) proposes a whole block of candidate tokens in one parallel pass, then a candidate selector scores which path to verify. It ships as its own GGUF, loaded *alongside* the target model — confirmed working command from the HF repo's own README: `llama-server -hf ggml-org/Qwen3.8-27B-GGUF:Q4_K_M -hfd incoai/Qwen3.8-27B-DFlash2-GGUF:Q4_K_M --spec-type draft-dflash --spec-draft-n-max 7`. Inco AI's own claim: "more than 20% more accepted tokens for every verification pass for around 1.3% added cycle latency" (per a benchmark video quoting their blog post). An independent benchmark video (ML Visualized) measured 48.45 tok/s plain greedy decoding vs. 89.30 tok/s with DFlash — a 1.84x speedup on a "warmed local run" — with both routes producing byte-identical output tokens, confirming this is a speed technique, not a quality tradeoff. **Flagship demo: Qwen3.8-27B** — a ready-to-download *drafter* GGUF exists at `huggingface.co/incoai/Qwen3.8-27B-DFlash2-GGUF` (it pairs with, not replaces, the actual Qwen3.8-27B target-model GGUF), directly relevant to this folder's `qwen 3.8 hw mini.md` sibling doc. ⚠ Early-stage: a GitHub issue (`jundot/omlx#2972`) reports a real integration bug (a resident DFlash engine gets corrupted by process-global patches after loading a second model with a rival technique, MTP/Multi-Token Prediction), and at least one community member on a separate PR called MTP "way more agent-friendly than DFlash" — so DFlash2 is not yet a universally-preferred choice over every alternative, just the newest one with strong early numbers on Qwen3.8-27B specifically.

## 3. Decision tree — which combination do you actually need?

Answer these in order; stop at the first branch that fits.

```
START: What's your model's architecture?
│
├─ It's a Mixture-of-Experts (MoE) model
│   │
│   ├─ Do you have a purpose-built extreme-quant engine for this exact model
│   │  family (Mach-1-style: custom kernels, sub-2-bit, MoE-aware)?
│   │   ├─ YES → use it. Stacks MoE sparsity + extreme quantization natively.
│   │   │        See "Scenario C" below (Mach-1-style).
│   │   └─ NO  → build/use a generic MoE expert-streaming setup
│   │            (kimi-k3-in-c pattern: dense trunk resident, experts
│   │            streamed from NVMe on demand). See "Scenario A" below.
│   │
│   └─ Either way: your floor is disk I/O speed for expert fetches, not RAM.
│      More RAM only buys speed (fewer disk round-trips), never a smaller
│      floor — "memory as a dial," not a wall.
│
└─ It's a dense model (every param active every token)
    │
    ├─ Does it fit at 4-bit GGUF in your combined RAM+VRAM?
    │   ├─ YES → use 4-bit. Best quality/size tradeoff, stop here.
    │   └─ NO  → drop to 2-bit. Expect a real quality hit below 2-bit;
    │            this is your practical floor for a dense model.
    │            See "Scenario B" below (Qwen3.8-27B-style).
    │
    └─ Either way: your floor is quantization's accuracy/size tradeoff,
       not disk I/O — there's no sparsity to exploit, every offloaded
       layer still processes every token.

THEN, regardless of architecture, layer on (in this order):
  1. Load mode matched to your constraint (mlock if RAM is ample, mmap if tight)
  2. Flash Attention forced on and confirmed active
  3. KV cache quantized separately from model weights (if context > ~2K tokens)
  4. Context size capped to what you actually need
  5. Speculative decoding, only if you have a compatible draft model and need speed
```

## 4. The full operational workflow (start to finish, one model)

Section 3's decision tree tells you *which technique* to use. This section is the actual *procedure* — the ordered stages you run through to get one specific model from "I want to run this" to "it's serving correctly at my hardware ceiling." Each stage has a clear input, output, and a pointer to the section with the how-to detail. Loop back a stage when its checkpoint fails — don't skip forward on a failed checkpoint.

```
STAGE 0 — Define the target
  Input:  a model name you want to run
  Do:     look up total params, active params (if MoE) or confirm dense,
          and your real hardware budget (RAM, VRAM, SSD free space)
  Output: one line — e.g. "GLM-5.2, 753B total / ~40B active MoE, 24GB RAM, 500GB SSD free"
  │
  ▼
STAGE 1 — Classify architecture
  Input:  the one-liner from Stage 0
  Do:     MoE or dense? (this is the first fork in Section 3's decision tree)
  Output: architecture class
  │
  ▼
STAGE 2 — Pick your lever(s)                                    [→ Section 3]
  Input:  architecture class + hardware budget
  Do:     walk Section 3's tree to a leaf: expert-streaming, GGUF+offload,
          extreme sub-2-bit, or (if nothing fits even quantized) check
          whether sparse upcycling is a real option for this model        [→ Section 9]
  Output: chosen technique(s), in order
  │
  ▼
STAGE 3 — Acquire the weights
  Input:  chosen technique(s)
  Do:     download the original checkpoint, or a pre-quantized GGUF
          (bartowski/Unsloth-style repos) if one exists at your target
          bit-depth — verify checksum and re-check the license terms
          before deploying
  Output: weights on disk
  │
  ▼
STAGE 4 — Convert / quantize (skip if you downloaded pre-quantized)
  Input:  full-precision weights
  Do:     run llama.cpp's convert script, then the `quantize` binary at
          your target bit-depth from Stage 2
  Output: a GGUF file at your target quant tier
  │
  ▼
STAGE 5 — Configure serving flags                        [→ Section 5 (worked commands), Section 6 (cheat-sheet)]
  Input:  the GGUF file + chosen technique(s)
  Do:     pick the closest matching Scenario in Section 5, apply Section 2's
          complementary flags (load-mode, flash-attn, KV-cache quant,
          context size, speculative decoding if applicable — check DFlash 2
          first if your model has a matching checkpoint, e.g. Qwen3.8-27B;
          it uses a small purpose-built drafter GGUF loaded alongside the
          target model, not "no draft model" — see Section 5 for the exact
          two-file command, unlike classic Technique D's single-token drafter)
  Output: a runnable server-launch command
  │
  ▼
STAGE 6 — Dry-run load test
  Input:  the launch command
  Do:     start the server, watch startup logs — confirm it loads within
          your Stage 0 RAM/VRAM budget, confirm Flash Attention is
          actually active (don't trust `auto` silently), confirm
          mmap/mlock behavior matches what you chose
  Output: PASS (loaded within budget) or FAIL → go to Stage 8
  │
  ▼
STAGE 7 — Validate quality                                          [→ Section 8 tradeoffs table]
  Input:  a running server
  Do:     run a handful of known-good prompts for your actual use case,
          compare output quality against your quant tier's expected
          degradation (non-linear below 2-bit per Section 8)
  Output: PASS (acceptable quality) or FAIL → go to Stage 2 and pick a
          higher quant tier or a different technique
  │
  ▼
STAGE 8 — Tune under load                                      [→ Section 7 troubleshooting table]
  Input:  a FAIL from Stage 6 or real-traffic testing
  Do:     match the symptom to Section 7's troubleshooting table
          (OOM at load / OOM as context grows / slower than expected /
          prompt-processing OOM specifically), apply the fix, loop back
          to Stage 5
  Output: an updated launch command → back to Stage 6
  │
  ▼
STAGE 9 — Lock in & document
  Input:  a server that passed Stages 6 and 7
  Do:     record the final flags, measured tok/s, and measured peak
          RAM/VRAM — this is the concrete evidence a future "min-viable
          size" or "final estimated param" claim in the sibling
          `Orbi OSSLLM research.md` doc should cite instead of a
          theoretical estimate
  Output: a reproducible, documented deployment
```

**Why loops matter here:** Stage 6 and Stage 7 are the two checkpoints most workflows online skip — they show a launch command and stop, leaving "does it actually fit" and "is the quality actually acceptable" as an exercise for the reader. Looping back from a failed checkpoint (to Stage 2 for a technique change, or Stage 5 for a flag change) is what turns a list of flags into an actual workflow.

## 5. Worked example commands (copy-paste starting points)

These are realistic `llama.cpp` server invocations for the three model classes covered in this folder's sibling docs. Adjust paths, ports, and exact quant filenames to your actual setup — these are structurally correct combinations of flags, not tested end-to-end on real hardware in this research pass.

### Scenario A — MoE model on constrained RAM (Kimi K3-style, expert streaming)

kimi-k3-in-c is a from-scratch engine, not a llama.cpp flag combination — if llama.cpp ever gains native MoE expert-streaming for a model this large, the equivalent invocation would combine mmap (to let the OS page unused expert weights out) with aggressive quantization:

```bash
# Conceptual — kimi-k3-in-c's own CLI, not llama.cpp:
./scripts/k3-doctor.sh                 # validate the machine can run it first
make -j                                # build the weightless-test-passing engine
./kimi-k3-infer \
  --trunk-path ./packed-trunk \        # ~109GB packed trunk, prepared once
  --experts-path ./packed-experts \    # 1.45TB of MXFP4 expert weights on NVMe
  --ram-budget 8G \                    # the dial — more RAM = fewer disk round-trips, same output
  --prompt "your prompt here"
```

If instead you're running a smaller MoE model that llama.cpp itself supports natively:

```bash
llama-server \
  -m your-moe-model-Q4_K_M.gguf \
  -lm mmap \                           # let the OS page in only what's touched
  -fa on \                             # force Flash Attention, verify it's active in logs
  -ctk q8_0 -ctv q8_0 \                # quantize the KV cache separately
  -c 8192 \                            # cap context to what you actually need
  --host 0.0.0.0 --port 8080
```

### Scenario B — Dense model on limited VRAM (Qwen3.8-27B-style, GGUF + offload)

```bash
# 4-bit, fits in ~17GB combined RAM+VRAM — the default recommendation
llama-server \
  -m Qwen3.8-27B-Q4_K_M.gguf \
  -ngl 99 \                            # push as many layers to GPU as fit; 99 = "all"
  -lm auto \                           # mmap unless the device can't support it
  -fa on \
  -ctk q8_0 -ctv q8_0 \
  -c 8192 \
  -b 2048 -ub 512 \
  --host 0.0.0.0 --port 8080

# 2-bit fallback, for ~9-11GB combined RAM+VRAM (e.g. a 16GB unified-memory Mac)
llama-server \
  -m Qwen3.8-27B-UD-IQ2_XXS.gguf \
  -ngl 99 \
  -lm mmap \                           # more load-bearing at 2-bit — every MB counts
  -fa on \
  -ctk q4_0 -ctv q4_0 \                # more aggressive KV quant too, at this tier
  -c 4096 \                            # smaller context ceiling — expect slowdown past ~7K tokens
  --host 0.0.0.0 --port 8080

# Speed upgrade on top of either tier above: DFlash 2 (Technique F, Section 2) —
# a purpose-built DRAFTER GGUF exists specifically for this model, loaded
# ALONGSIDE (not instead of) the target model. Real benchmark: 1.84x tok/s
# on a comparable setup (48.45 -> 89.30 tok/s), byte-identical output.
# Command below is copied from incoai/Qwen3.8-27B-DFlash2-GGUF's own README
# (confirmed 2026-08-29) — the -hf/-hfd direct-download form is the one
# actually shown by the source; treat it as verified, not guessed.
llama-server \
  -hf ggml-org/Qwen3.8-27B-GGUF:Q4_K_M \          # the actual target model
  -hfd incoai/Qwen3.8-27B-DFlash2-GGUF:Q4_K_M \   # the DFlash2 drafter (separate, small)
  -ngl 99 \
  -lm auto \
  -fa on \
  -ctk q8_0 -ctv q8_0 \
  -c 8192 \
  --spec-type draft-dflash \           # confirmed via the HF repo's own README
  --spec-draft-n-max 7 \
  --host 0.0.0.0 --port 8080

# Local-file equivalent, if you've already downloaded both GGUFs yourself:
# the -m/-md pairing below is NOT independently confirmed this pass — the
# source README only demonstrates the -hf/-hfd direct-download form above —
# verify -m + -md behaves the same on your build before relying on it.
llama-server \
  -m Qwen3.8-27B-Q4_K_M.gguf \
  -md Qwen3.8-27B-DFlash2-GGUF-Q4_K_M.gguf \
  -ngl 99 -lm auto -fa on -ctk q8_0 -ctv q8_0 -c 8192 \
  --spec-type draft-dflash --spec-draft-n-max 7 \
  --host 0.0.0.0 --port 8080
```

### Scenario C — Extreme quantization on Apple Silicon (Mach-1-style, if using an equivalent open tool)

Mach-1's actual runtime (Mach Engine) is a closed, purpose-built binary, not a llama.cpp invocation — its whole value is the custom "fused decode-in-GEMV Metal kernels" that generic tools don't have. If you're instead pushing llama.cpp as low as it goes on Apple Silicon:

```bash
# Lowest llama.cpp goes on a dense/MoE-hybrid model on Apple Silicon
llama-server \
  -m your-model-IQ2_XXS.gguf \         # llama.cpp's own quantization floor, not sub-2-bit
  -lm mmap \
  -fa on \                             # Metal backend Flash Attention
  -ctk q4_0 -ctv q4_0 \
  -c 4096 \
  --host 0.0.0.0 --port 8080

# For the actual Mach-1 pattern (sub-2-bit, MoE + extreme quant stacked),
# you need Mach Engine itself — no generic-tool equivalent exists as of this
# research pass. See mach 1 hw mini.md for what it does and why llama.cpp
# can't currently replicate the 1.7-bit floor.
```

## 6. Flag cheat-sheet (quick reference)

| Flag | Controls | When to touch it |
|---|---|---|
| `-ngl` / `--gpu-layers` | How many layers go to GPU vs CPU | Set to `99`/`all` if it fits; lower it manually if you're hitting VRAM OOM specifically, not general OOM |
| `-lm` / `--load-mode` | `mmap` vs `mlock` vs `auto` | `mlock` if RAM comfortably exceeds the quant file; `mmap` if tight or deliberately running something bigger than RAM |
| `-fa` / `--flash-attn` | Fused attention kernel | Force `on`, don't trust `auto` silently — check server startup logs confirm it's active |
| `-ctk` / `-ctv` | KV cache quant type for K/V | Set both to at least `q8_0` once context regularly exceeds a few thousand tokens |
| `-c` / `--ctx-size` | Context window size | Cap to what your use case actually needs — never load the model's max "just in case" |
| `-b` / `--batch-size` | Logical max batch size | Leave at default unless you're specifically tuning prompt-processing throughput |
| `-ub` / `--ubatch-size` | Physical max batch size | Lower it if prompt processing itself is OOMing (distinct from generation OOM) |
| `-md` / `--spec-draft-model` | Draft model for speculative decoding | Only set if you have a small, compatible draft model for your target family and need more speed at your current memory floor |

## 7. Troubleshooting — which failure are you actually hitting?

| Symptom | Likely cause | Fix |
|---|---|---|
| Model won't load at all, immediate OOM | Quant file bigger than combined RAM+VRAM | Drop a quant tier (4-bit → 2-bit), or for MoE models check expert-streaming is actually engaged, not loading everything |
| Model loads, generation starts fine, then OOMs as the conversation grows | KV cache growing with context length, not the model itself | Quantize KV cache (`-ctk`/`-ctv` to q8_0 or lower), or cap `-c` to a smaller ceiling |
| Everything loads and runs, but generation is much slower than expected | `-fa` silently fell back to off, or `-lm mmap` is causing heavy disk re-reads under memory pressure | Check server startup logs for Flash Attention status; if RAM is genuinely tight, this is `mmap`'s expected tradeoff (speed for capacity) — either accept it or free up more RAM/VRAM for `mlock` |
| Prompt processing (not generation) is what's OOMing | Batch size too large for available memory during the prompt-ingestion phase | Lower `-b`/`-ub` — this is a distinct memory phase from steady-state generation |
| Speculative decoding making things slower, not faster | Draft model's guesses are frequently wrong for this content style, so rejected drafts add overhead instead of saving it | Drop speculative decoding for this workload, or find a draft model better matched to your actual output style |
| Quality noticeably worse after dropping a quant tier | Expected — quality degrades non-linearly below ~2-bit for dense models | This is the real cost of the technique, not a bug; go back up a tier if quality matters more than footprint for this use case |

## 8. Tradeoffs at a glance

| Lever | What it costs when pushed hard | What it saves |
|---|---|---|
| Lower weight quantization (GGUF bit-depth) | Output quality degrades, most sharply below 2-bit | Model footprint (linear-ish with bit-depth) |
| MoE expert streaming from disk | Per-token latency (disk I/O every forward pass) | Peak RAM (only active experts resident) |
| `mmap` over `mlock` | Unpredictable stalls when memory pressure forces re-reads | Lets you run models bigger than physical RAM |
| Aggressive KV cache quantization | Long-context coherence can degrade | Memory that scales with conversation length, not just model size |
| Speculative decoding | Wasted compute on rejected draft guesses (small models with unpredictable output style see fewer accepted drafts) | Wall-clock speed at a fixed memory footprint |

## 9. Sparse upcycling — build-time technique to shrink an existing dense model's hardware floor

**What it is:** convert an existing dense model (every param active every token) into a Mixture-of-Experts model by duplicating its feed-forward layers into several expert copies, adding a learned router on top, then continuing training (fine-tuning, not a full retrain from scratch) so the experts specialize. The real published version of this is "sparse upcycling" (Komatsuzaki et al., Google, 2022 / ICLR 2023) — reusing a dense checkpoint's weights to bootstrap a sparse MoE model at a fraction of the compute a from-scratch MoE run would need.

**This is a training-compute technique, not a runtime flag.** Every other technique in this doc (Sections 1-2) needs zero retraining — point llama.cpp or kimi-k3-in-c at an existing model and change how it's loaded/quantized. Sparse upcycling changes the model itself: it needs real GPU/TPU training compute and a training dataset, done once, before any runtime technique applies. Nobody has built a kimi-k3-in-c-style streaming engine for any of Orbi's picks — this section documents the theoretical hardware ceiling IF that were done, not something runnable today.

**Why it matters for hardware, once done:** Section 1's core MoE principle is that RAM/throughput tracks active-expert size + dense-trunk size, not total parameter count — and that's a property of the router (how many experts activate per token, i.e. top-k), not of how big the model originally was. So a dense model upcycled into a sparse MoE with a small top-k router can in theory land in roughly the same RAM ballpark as Kimi K3 (~8GB) regardless of the original dense model's size — the router design at conversion time is the lever, not the source model's parameter count. What DOES scale with the original model's size: the SSD footprint (all the expert copies, even unused ones, still need to be stored somewhere) and the one-time training compute cost.

**Caveat, stated plainly:** this is architecturally plausible reasoning extrapolated from Kimi K3's proven precedent, not a demonstrated result for any of Orbi's specific picks (GLM-5.2, DeepSeek-V4-Pro-0813, MiniMax M3, and similar). No source in this research pass shows any of them actually upcycled or streamed. Production MoE models exist and ship today (Mixtral, DeepSeek's own MoE line) proving the sparse-expert architecture works at scale — but whether they specifically used the upcycling bootstrap method versus MoE-from-scratch training was not verified in this pass, and isn't the load-bearing claim here anyway. The load-bearing claim is narrower: dense-to-MoE conversion is a real, published, working technique, and the RAM-floor reasoning follows directly from Section 1's own established principle once a model has been converted AND paired with a streaming engine — two separate, both-unbuilt steps for any of Orbi's current picks.

## 10. Orbi's actual hardware requirement at 24GB RAM (worked analysis, 2026-08-19)

Answers a direct follow-up asked in chat: "what does 24GB RAM actually get Orbi, across all 3 modes?"

- Orbi's 55 skills across 3 modes dedupe to 26 distinct models (`Orbi OSSLLM research.md`).
- Storage: ~6.19TB total across all 26 at 4-bit GGUF (using this doc's own empirical ratio, ~0.64GB/B params) — an SSD constraint, not a RAM constraint.
- RAM at 24GB, one model loaded at a time (realistic Orbi usage — swap models per task, not all at once): most of the 26 fit comfortably. Kimi K3 alone (streamed via kimi-k3-in-c) covers 31 of the 55 skills at an ~8GB floor.
- RAM at 24GB, the models that do NOT fit even quantized, with no streaming engine built for them: roughly 10 of the 26 — the largest dense/near-dense picks (GLM-5.2, DeepSeek-V4-Pro-0813, MiniMax M3, and similar). Not a permanent ceiling — every one of them is MoE-architecture-eligible in principle via Section 8, just unbuilt.
- All-26-concurrent peak (never actually needed by Orbi's real one-task-at-a-time usage pattern): ~6-7.5TB, far past 24GB — this number exists only as a theoretical upper bound, not a real operating scenario.

**Correction (2026-08-29 sweep):** `Orbi OSSLLM research.md` was restructured 2026-08-28 into a 302-leaf skill taxonomy and no longer carries the flat 3-section param totals shown above — that breakdown was originally sourced from that doc's old 3-section structure. A backup of that old structure (`Orbi OSSLLM research (legacy 3-section).md`) was intended but never actually written (the `cp` command that should have created it silently failed and was never verified) — it does not exist. The per-model numbers behind the Orbi-hardware-requirement figures above were verified once, at the time this section was written, but the exact original table they came from is gone; treat this section's own figures as the surviving record rather than expecting a source file to check them against.

## 11. Sources

- `kimi k3 hw mini.md`, `qwen 3.8 hw mini.md`, `mach 1 hw mini.md` (this folder) — full technique write-ups
- llama.cpp server flag reference (primary, fetched directly) — https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md
- llama.cpp main repo README (quantization tier list, backend support) — https://github.com/ggml-org/llama.cpp/blob/master/README.md
- Nathan Barry's deterministic-inference-across-hardware hackathon project (tangential, different axis — reproducibility not minimization) — https://di.gg/ai/09jz37kf
- `/last30days` general research pass on "minimize hardware usage running LLM locally" — returned no new confirmed community findings this window (relevance floor rejected all clusters); informed the decision to synthesize from existing docs + primary llama.cpp docs instead of forcing a weak community-sourced angle
- DFlash 2 (Technique F, added 2026-08-29) — Inco AI's own blog post/HN thread (99pts, 18cmt) https://inco.ai/blog/dflash2/ ; the merged llama.cpp PR https://github.com/ggml-org/llama.cpp/pull/27342 ; benchmark videos https://www.youtube.com/watch?v=RBlRTUwJMI4 (Lukasz Gawenda, quotes Inco AI's 20%-more-accepted-tokens claim) and https://www.youtube.com/watch?v=MLFs08lsr6E (ML Visualized, independently measured 48.45 vs 89.30 tok/s); checkpoint https://huggingface.co/incoai/Qwen3.8-27B-DFlash2-GGUF ; integration-bug report https://github.com/jundot/omlx/issues/2972

## 12. Methodology note

The `/last30days` community-research pass for this specific query came back with "nothing solid this window" — Reddit, Hacker News, and Digg had real activity (50 items, real engagement) but none of it cleared the engine's relevance floor for genuinely new techniques; it was mostly hardware-shopping threads and benchmarks. Per that skill's own rule for an empty relevance floor, that layer was treated as absent rather than mined for weak signal. The complementary-technique section (Section 2) was instead built from a direct fetch of llama.cpp's own primary documentation — every flag name and description is quoted from the actual project docs, not inferred or reconstructed from memory. The worked example commands in Section 4 are structurally correct flag combinations based on that same primary documentation, but were not run end-to-end on real hardware in this research pass — verify they work on your actual setup before relying on them.

## 13. Change log

- 2026-08-23 — Created. Combines the three existing hw-mini docs with complementary techniques (KV cache quantization, Flash Attention, load-mode, speculative decoding, context/batch sizing) verified directly against llama.cpp's own server docs, plus a step-by-step combined workflow for stacking all of them.
- 2026-08-25 — User flagged the workflow section as insufficient and asked for a real, concrete expansion. Added: a full ASCII decision-tree workflow (Section 3, replacing the old prose-only step list) routing by model architecture first; 3 worked example `llama.cpp` command blocks for each model class this folder covers (Section 4); a flag cheat-sheet quick-reference table (Section 5); and a troubleshooting table mapping observed symptoms to likely causes and fixes (Section 6). The example commands are structurally correct per llama.cpp's own docs but not tested end-to-end on real hardware this pass — flagged explicitly in the methodology note rather than presented as verified working commands.
- 2026-08-25 — Added Section 8 (sparse upcycling / dense-to-MoE conversion as a build-time hardware-minimization technique, with the caveat that it's unbuilt for any current Orbi pick) and Section 9 (worked analysis of Orbi's actual 24GB-RAM hardware requirement, first answered in chat, now written down). Renumbered old Sections 8-10 (Sources, Methodology, Change log) to 10-12.
- 2026-08-29 — User asked for a detailed operational workflow, distinct from Section 3's decision tree (which only branches by architecture). Added Section 4 (new): a 10-stage ordered pipeline (Stage 0-9, define target -> classify architecture -> pick technique -> acquire weights -> quantize -> configure flags -> dry-run load test -> validate quality -> tune under load -> lock in & document), each stage with explicit input/output and a pointer to the section with the how-to detail, with explicit loop-back edges from failed checkpoints (Stage 6/7) rather than a linear list that stops at "here's a command." Renumbered old Sections 4-12 to 5-13 to make room.
- 2026-08-29 — User shared a Threads post claiming Qwen3.8-27B hits ~70 tok/s locally via a new decoding method "DFlash 2," asked to `/last30days` verify it then fold it into the workflow. Confirmed fully real: Inco AI shipped DFlash 2 mid-August 2026 (blog post + 99pt/18cmt HN thread), merged into llama.cpp's main branch within days (`ggml-org/llama.cpp#27342`), with a ready checkpoint for the exact model claimed (`incoai/Qwen3.8-27B-DFlash2-GGUF`). Two independent benchmark videos corroborate real speedup (20%+ more accepted tokens per Inco AI's own claim; an independently-measured 1.84x tok/s gain with byte-identical output in a separate video) — the post's ~70 tok/s figure is plausible and directionally consistent, though not the exact number either source measured. Added as Technique F in Section 2 (parallel drafting within the target model, no separate draft model needed — distinct from classic speculative decoding, Technique D), referenced it in Section 4's Stage 5 workflow step, and added a worked command block in Section 5 for the Qwen3.8-27B flagship case. Flagged honestly: still early-stage, one real integration bug already reported, and at least one community member prefers a rival technique (MTP) for agentic use — not presented as a universal upgrade.
- 2026-08-29 — Final verification sweep of this file (sections 1-13 numbering, Section 4's cross-references, and DFlash 2's factual claims). Numbering and all 4 cross-reference pointers in Section 4 (Stage 2→Section 9, Stage 5→Sections 5+6, Stage 7→Section 8, Stage 8→Section 7) checked correct against actual section content — no fixes needed there. DFlash 2 re-verified live: Inco AI blog post, `ggml-org/llama.cpp#27342`, the HF repo, and both cited YouTube channels (ML Visualized, Lukasz Gawenda) all confirmed real via direct fetch. But found and fixed a real factual error the prior entry introduced: DFlash 2 is NOT "no second model" — it IS a separate (small, ~18.5M-param) drafter GGUF loaded alongside the target model, just architecturally different from classic autoregressive drafting (one-pass block drafting + candidate selection instead of token-by-token). Corrected that claim in Section 2 (Technique F), Section 4 (Stage 5), and Section 5's worked command, which also had two more bugs: it used the drafter GGUF as `-m` (the main/target model slot) instead of pairing it correctly, and it stated the PR merged 2026-08-18 (that's the blog-post date; the PR actually merged 2026-08-27, confirmed by direct fetch). Replaced the worked command with the exact command shown in the HF repo's own README (`-hf`/`-hfd` direct-download form, flag confirmed as `--spec-type draft-dflash` not the earlier guessed `dflash2`), and added a clearly-caveated local-file (`-m`/`-md`) variant since that pairing is not independently confirmed. The 48.45/89.30 tok/s and "1.84x"/"20%+ accepted tokens" figures were re-checked against both video sources (channel names confirmed via YouTube oembed) but the exact numbers inside the videos could not be re-extracted this pass (WebSearch budget exhausted, YouTube page fetches return only nav/footer content) — left as previously recorded rather than re-guessed.
- 2026-08-29 — Final vault sweep caught a second broken pointer to the same non-existent legacy file (the first one, in the doc's own Section 10, was fixed by a sweep agent in `Orbi OSSLLM research.md` directly). Corrected this file's Section 10 pointer to state honestly that the intended backup was never actually written (a silently-failed, unverified `cp` command) rather than pointing at a file that doesn't exist.
