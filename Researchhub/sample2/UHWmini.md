# UHWmini — Unified Hardware-Minimisation & Pace Playbook

**Target machine:** Mac mini **M4**, 10-core CPU / 10-core GPU, **24 GB unified memory**, **8 TB SSD**
**Scope confirmed with the user:** three tiers (Daily / Heavy / Ceiling) × all four workloads
(agentic coding, long-doc & RAG, general chat, vision)
**Built:** 2026-09-01 · Sample 2 · self-contained

---

## READ THIS FIRST — the finding that reorganises everything

**Most hardware-minimisation tooling is CUDA-path. Your machine is not.**

The tools you named are real and good, but they are not all *yours*. TurboQuant ships **Triton
kernels + vLLM integration** — both NVIDIA-path. KTransformers' famous result is a 671B model on
*a 24 GB **GPU** plus system RAM*, which is not what a unified-memory Mac is.

On Apple Silicon a different stack wins, and one technique **inverts**:

> **Speculative decoding is a net *loss* in llama.cpp on Metal, and a large *win* in MLX.**
> Measured: MTP speculative decoding on Metal is **11% slower even at 100% draft acceptance**, and
> **28% slower at `n_max=6`** with 43% acceptance. Cause: *"each draft-verify step launches a
> separate Metal GPU kernel, and on Apple Silicon that cost is larger than the time the speculation
> saves."* MLX **fuses verification into the same compute graph**, so there is no per-token dispatch
> penalty — *"run the identical speculative idea through MLX instead of llama.cpp and it flips from a
> loss to a large win."* Apple's own Recurrent Drafter hit **2.3× on Metal**.

**Direct answer to your DFlash 2 question: yes, pursue speculative decoding — but through MLX, not
llama.cpp.** Running DFlash 2's GGUF build under llama.cpp on your M4 is the configuration most
likely to make things *slower*.

**Second structural finding, and it constrains your Ceiling tier:** **MoE expert streaming from SSD
is not shipped in MLX.** It is an **open feature request** ([`ml-explore/mlx-lm` issue #1438](https://github.com/ml-explore/mlx-lm/issues/1438)),
filed precisely to run models exceeding unified memory. Your 8 TB SSD is the right hardware for that
idea; the MLX software to exploit it does not exist yet. One project does it today on macOS/arm64 —
see Tier 3.

---

## 1. Your actual memory budget

| Quantity | Value | Note |
|---|---|---|
| Unified memory | 24 GB | shared by CPU **and** GPU |
| **Practically addressable by Metal** | **≈ 18–19 GB by default — raisable, see §5b** | ~79% observed on Apple Silicon; a 16 GB Mac reports a **12.71 GB** Metal ceiling |
| Left for OS + apps | ~5–6 GB | do not plan to use it |
| SSD | **8 TB** | your biggest asymmetric advantage — see Tier 3 |

**Plan against ~18 GB, not 24 GB.** Every budget below uses that. Get the real number: llama.cpp
prints `recommendedMaxWorkingSetSize` at startup.

**The budget equation, which is the whole game:**

```
  18 GB  ≥   weights  +  KV cache  +  (drafter, if speculating)  +  (vision projector, if used)
```

Everything in this document shrinks one of those four terms, or buys speed with one.

---

## 2. The tool catalogue

Your five, verified, plus what the research added. **The Mac column is the one that matters.**

### Layer 1 — Weight quantisation (shrinks `weights`)

| Tool / method | What it does | Mac (M4) | Verified |
|---|---|---|---|
| **llama.cpp / GGUF** *(yours)* | K-quants: precision per layer by importance. Q4_K_M ≈ **92% quality retained** | ✅ native Metal | ✓ |
| **MLX / mlx-lm** | Apple's own framework, built for unified memory | ✅ **best on Mac** | ✓ |
| **AWQ** | activation-aware; fastest under vLLM (741 tok/s, Marlin kernel) | ❌ vLLM/CUDA | ✓ |
| **GPTQ** | mature, huge pre-quantised library | ❌ GPU path | ✓ |
| **bitsandbytes** | **only option supporting training (QLoRA)** | ❌ CUDA | ✓ |
| **AQLM** | vector quant, learnable 8D codebooks; `1×16` = one codebook of 2¹⁶ per linear layer | ❌ | ✓ |
| **QuIP#** | Hadamard incoherence + lattice codebooks | ❌ | ✓ |
| **QTIP** | SOTA scalar quant, reaches vector-quant parity | ❌ | ✓ |
| **EXL2 / EXL3** | method not format; safetensors-based | ❌ GPU path | ✓ |
| **Additive / sub-2-bit** | ~1.7 bits/weight, add-subtract-only matmul, fused decode-in-GEMV Metal kernels | ✅ **Apple Silicon only** | ✓ |

**The quality cliff, stated once:** at **≥4 bits every method lands close to full precision.** In the
**3–4 bit** band vanilla GPTQ falls behind and modern scalar methods have caught up to vector
methods. Below 3 bits you are trading real quality — fine, but choose it deliberately.

### Layer 2 — KV-cache compression (shrinks `KV cache` — your biggest lever at long context)

| Tool / method | What it does | Mac (M4) | Verified |
|---|---|---|---|
| **TurboQuant** *(yours)* | near-optimal KV quant, **3-bit keys / 2-bit values**, two-stage rewrite; **~4× more context** in the same memory. ICLR 2026 | ⚠️ **Triton + vLLM** — not Mac today | ✓ |
| **KIVI** *(yours)* | asymmetric quantised cache (per-channel keys, per-token values) | ⚠️ research impl | ✓ |
| **llama.cpp `--cache-type-k/v q8_0`** | brute-force cache quant, **~50% cut** | ✅ **works today** | ✓ |
| **SnapKV** | selects clustered important tokens per attention head | ⚠️ research | ✓ |
| **PyramidKV** | pyramidal funnelling; **beats H2O, SnapKV, StreamingLLM at small cache sizes** | ⚠️ research | ✓ |
| **xKV** | cross-layer compression via aligned singular vectors; **89.22% avg**, **+1.7% over KIVI-2** on Llama-3.1-8B | ⚠️ research | ✓ |
| **Quest** | query-aware sparsity for long context | ⚠️ research | ✓ |
| **H2O / StreamingLLM** | heavy-hitter / sink-token eviction — the older baselines | ⚠️ research | ✓ |
| **KVCache-Factory** | **unified playground** implementing all of the above — start here to compare | ⚠️ research | ✓ |
| **Fast-TurboQuant** | multiplier-free **online** vector quantisation (arXiv 2606.21448) | ⚠️ new | ✓ |

### Layer 3 — Offload & streaming (moves `weights` off RAM entirely)

| Tool / method | What it does | Mac (M4) | Verified |
|---|---|---|---|
| **kimi-k3-in-c** | **2.78T model in 8.24 GB RAM**, C99, experts multiplied straight from packed 4-bit on disk | ✅ **macOS/arm64 supported** | ✓ |
| **KTransformers** | hybrid CPU/GPU MoE; 671B on one 24 GB **GPU** + RAM; v0.6.3 supports DeepSeek-V3/R1, Kimi K2/K2.5, GLM-5/5.2, Qwen3-MoE | ⚠️ **Metal support claimed but suspect — see gaps** | ⚠️ |
| **FlashMoE** | SSD expert offload with **ML-based cache replacement** blending recency + frequency (arXiv 2601.17063) | ⚠️ research | ✓ |
| **HOBBIT** | mixed-precision expert offloading | ⚠️ research | ✓ |
| **PIPO** | pipelined offloading for consumer devices | ⚠️ research | ✓ |
| **NPUMoE** | MoE on **Apple Silicon NPUs** — static compute to ANE, CPU/GPU fallback for dynamic ops (arXiv 2604.18788) | ✅ Apple-targeted, research | ✓ |
| **mlx-lm expert streaming** | the missing piece | ❌ **open feature request #1438** | ✓ |
| **llama.cpp `--n-cpu-moe` / `-ot`** | keep MoE experts on CPU, attention on GPU | ✅ works; less relevant on unified memory | ✓ |

### Layer 4 — Pace / decoding (buys speed, sometimes *costs* memory)

| Tool / method | What it does | Mac (M4) | Verified |
|---|---|---|---|
| **DFlash 2** | **block-diffusion drafter** — drafts a whole block in one pass, top-k per position, selector traces one path. **236.1 tok/s / 3.43× on H200**. Output identical | ⚠️ **use via MLX, not llama.cpp** | ✓ |
| **MLX fused speculative decoding** | verification fused into one compute graph — **no per-token dispatch penalty** | ✅ **the right path for you** | ✓ |
| **Recurrent Drafter** (Apple) | **2.3× on Metal** | ✅ Apple research | ✓ |
| **llama.cpp `--spec-type draft-mtp`** | MTP speculative decoding | ❌ **net loss on Metal: −11% to −28%** | ✓ |
| **`--flash-attn`** | cuts attention memory; matters most when cache is a big share | ✅ | ✓ |
| **Prompt / prefix caching** | reuse the KV of a stable prefix across calls | ✅ | ✓ |

### Layer 5 — Retrieval (avoids spending context at all)

| Tool | What it does | Verified |
|---|---|---|
| **Turbovec** *(yours)* | **TurboQuant-compatible vector search + graph memory for constrained RAG** | ✓ |
| **LMCache** | KV-cache reuse layer across requests | ✓ |

> ### ⚠️ "Turbo Fieldfare" — I could not find it
> You listed it. **It does not appear in any source reachable from this session.** TurboQuant ✓ and
> Turbovec ✓ both verified; Turbo Fieldfare returned nothing. Possibilities: a misremembered name, a
> project too new or too private to be indexed, or an internal codename. **I am not going to invent
> an entry for it.** Send me a link or where you saw it and I will research it properly and add it.

---

## 3. The three tiers, sized for your 24 GB

### Tier 1 — DAILY (interactive, target 15+ tok/s)

**Runtime: MLX.** On a Mac mini M4 Pro, MLX ran Qwen3-Coder-30B-A3B at **~130 tok/s** vs **43 tok/s**
for Ollama-on-llama.cpp — a **3×** gap. Ollama itself switched to MLX in March 2026 and its decode
went **58 → 112 tok/s** on the same machine. MLX leads by **20–87% under 14B**.

| Budget item | Allocation |
|---|---|
| Weights | **8–12 GB** — a 14–27B class model at 4-bit, or a small MoE |
| KV cache | 3–5 GB (32–64K context) |
| Headroom | 2–3 GB |

**Add speculative decoding here** — via MLX, where it is a win.

### Tier 2 — HEAVY (best quality that still fits RAM, ~5–10 tok/s)

Push weights to the ceiling, shrink everything else.

| Budget item | Allocation |
|---|---|
| Weights | **15–17 GB** — 27B-class at 4-bit (Q4_K_M from lmstudio-community is **16.81 GB**, the smallest 4-bit) |
| KV cache | 1.5–2.5 GB, **quantised** `--cache-type-k q8_0 --cache-type-v q8_0` |
| Context | 16–32K — **not more** |

⚠️ **Known failure:** 4-bit Qwen3.8-27B on a **16 GB** Mac dies with
`failed to decode generation batch, res = -3`. You have 24 GB, so it fits — **with roughly 1–2 GB of
margin, not comfort.** If you see `res = -3`, drop one quant level. It does not degrade gracefully;
it crashes.

**Also viable here and much roomier:** a sub-2-bit additive 35B MoE at **~8.1 GB** —
Apple-Silicon-only, fused decode-in-GEMV Metal kernels so **no dequantised copy ever exists in
memory**, ~96% quality retention vs its own BF16 teacher. **8.1 GB of weights against an 18 GB
budget leaves ~10 GB of KV cache** — which is what actually buys long context.

### Tier 3 — CEILING (largest model physically runnable; seconds per token)

**This is where your 8 TB SSD stops being storage and becomes the feature.**

**kimi-k3-in-c** runs a **2.78-trillion-parameter** model on a single CPU by keeping **1.45 TB of
routed experts on disk**, multiplied straight out of packed 4-bit form, with the 93 dense layers
packed into one 109 GB sequential-access file. **macOS/arm64 supported.** Apache-2.0.

| Requirement | You have |
|---|---|
| 8 GB RAM minimum (8.24 GB measured peak) | **24 GB** ✅ |
| **~1.7 TB free storage** | **8 TB** ✅ |
| AVX2+FMA / arm64 | M4 ✅ |
| No GPU needed | ✅ |

**Expected pace on your box:** measured **26.5 s/token** at 8 GB, **24.2 s/token** at 32 GB. You sit
between → **roughly 24–26 s/token**. A 500-token answer ≈ **3.5 hours**.

The RAM dial buys little here: **8 GB → 128 GB is 16× the memory for a 4.7× speedup**, nearly flat
from 8→32 GB. **Your 24 GB is already on the flat part of that curve** — more RAM would not help
much; a faster SSD would.

**The genuinely elegant property:** output is **byte-identical across every memory configuration**.
Unlike quantisation, this memory dial costs **zero quality**. Purely time-for-space.

**Use it for:** an overnight question worth waiting for. Not a chat.

---

## 4. Per-workload budgets

Same 18 GB, allocated differently. This is the tradeoff you asked about.

### Agentic coding / tool use
Long sessions, many turns, growing context.
- **Weights 10–12 GB** · **cache 5–6 GB** · quantise the cache from the start
- **Prefix caching is the highest-leverage setting** — a stable system prompt plus tool definitions
  otherwise gets re-encoded every single turn
- MLX + fused speculative decoding — tool-call output is structured and highly predictable, which is
  exactly where a drafter's acceptance rate is highest

### Long-document / RAG
- **Cache dominates. Past ~100K tokens the cache is bigger than the weights.**
  Reference shape (27B-class): 8K → 0.5 GB · 32K → 2 GB · **131K → 8 GB** · **262K → 16 GB**
- **Prefer a model with hybrid/linear attention.** A 27B using linear attention in 48 of 64 layers
  needs **a quarter** of the cache a conventional 64-layer model does. That architectural choice
  beats every compression trick in Layer 2.
- **Retrieve instead of stuffing** — Turbovec + LMCache. Not putting a token in the window is
  cheaper than compressing it.
- ⚠️ **MLX caveat specific to this workload: MLX's advantage reportedly degrades past ~40K context.**
  For very long contexts, benchmark llama.cpp against MLX rather than assuming MLX wins.

### General chat / short tasks
- Context is cheap, so **spend nearly everything on weights**: 15–17 GB, cache ~1 GB at 8–16K
- Highest tokens/sec of any workload — where a 4-bit 27B feels good

### Vision / multimodal
- **Projector costs +0.63–0.93 GB** on top of weights — budget ~1 GB
- Pass `--mmproj`; if the server reports `modalities: text` on a vision model, the projector did not load
- Images eat context fast; keep the cache quantised

---

## 5. The workflow

```
STEP 0 — measure, don't assume
        llama.cpp prints recommendedMaxWorkingSetSize at startup. Use that number.
                        │
STEP 1 — pick the tier for THIS task
        interactive? ──► Tier 1        best answer that fits RAM? ──► Tier 2
        biggest possible, time irrelevant? ──► Tier 3 (SSD streaming)
                        │
STEP 2 — pick the runtime
        Mac, <30B  ──────────────► MLX            (20–87% faster under 14B)
        Mac, >=27B ──────────────► MLX or llama.cpp — converges, memory-bandwidth bound
        very long context (>40K) ─► BENCHMARK BOTH — MLX's edge reportedly fades
        Tier 3 ──────────────────► kimi-k3-in-c
                        │
STEP 3 — size weights first, at the HIGHEST quant that still leaves cache room
        >=4-bit if it fits — that is where quality stays near full precision
        3-bit if not  ·  sub-2-bit additive if you want maximum cache headroom
                        │
STEP 4 — size the cache for the workload  (section 4)
        quantise it: --cache-type-k q8_0 --cache-type-v q8_0   (~50% off)
        enable --flash-attn
                        │
STEP 5 — dry-run load test  <── FAILURE HERE IS NORMAL, LOOP BACK TO STEP 3
        RUN IT FOR 10 MINUTES, not 60 seconds (section 8). Watch memory
        pressure in Activity Monitor the whole time.
        res = -3  ──► weights exceed working set, drop one quant level
        3-4x slower than expected ──► file larger than addressable memory
                        │
STEP 6 — add speed, in this order
        a) prefix / prompt caching        <- free, biggest win in agentic loops
        b) --flash-attn
        c) speculative decoding VIA MLX   <- DFlash2-class; a LOSS in llama.cpp on Metal
        d) reasoning_effort: low          <- xhigh burns max_tokens before answering
                        │
STEP 7 — verify quality didn't quietly drop
        run your own 10-prompt set at the old and new settings. Quantisation
        failures are silent; nothing errors when a 2-bit model just gets worse.
                        │
STEP 8 — write down the winning config, and the number you measured
```

**Tuning-order rule, learned the hard way by others:** *"If you set a large context size and then
sweep `--n-cpu-moe`, you will find a much worse optimum than if you had set a smaller context
first."* **Tune offload at small context, then grow context.** Never the reverse.

**One more free win:** `--no-mmap` — one report measured system RAM use dropping **98% → 71% at the
same generation speed.** Worth testing on a memory-tight config.

---


### 5b. The one flag this document was missing — `iogpu.wired_limit_mb`

Recovered on the 2026-09-02 re-sweep from the very source whose link had been wrongly flagged as dead.

> **"The single most important tuning step is not a llama.cpp flag at all, it is
> `sudo sysctl iogpu.wired_limit_mb=N`."**

**This directly changes section 1 of this document.** The ~18 GB "practically addressable by Metal"
figure is **not a hardware limit — it is a default**, and `iogpu.wired_limit_mb` raises the ceiling on
how much unified memory Metal is allowed to wire down. On a 24 GB machine that is the difference
between fitting a 4-bit 27B comfortably and crashing with `res = -3`.

**Raise it deliberately and not to the maximum** — the OS and everything else still need memory, and
starving them will hang the machine rather than slow it. Increase in steps, test a real load at each
step, and keep several GB of headroom.

**The seven flags that actually matter on Apple Silicon**, from the same source:

```bash
-ngl 99 -fa 1 -c <ctx> -b 2048 -ub 2048 --cache-type-k q8_0 --cache-type-v q8_0
# plus, if you have memory headroom:
--mlock --prio 2
```

| Flag | Effect |
|---|---|
| `-ngl 99` | offload **all** layers to the Metal GPU — the value is clamped to the real layer count, so 99 just means "everything" |
| `-fa 1` | flash attention |
| `-c <ctx>` | context window |
| `-b 2048` / `-ub 2048` | batch and micro-batch |
| `--cache-type-k/v q8_0` | KV cache quantisation (already covered in §2.2) |
| `--mlock --prio 2` | only with headroom to spare |

> **And the warning that matters most:** *"Most other flags you find in tutorials were copied from
> x86 server documentation and **have no effect on M-series chips**."* Treat any Apple Silicon tuning
> advice that does not name Metal or `iogpu` as probably transplanted from a different platform.

### 5c. **DWQ — the single biggest quality win available to you**

Added 2026-09-02. **If you read one thing in this file, read this.**

MLX ships **learned quantization** methods that standard GGUF pipelines do not have
([`mlx_lm/LEARNED_QUANTS.md`](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LEARNED_QUANTS.md)):

| Method | What it does |
|---|---|
| `dynamic_quant` | fastest to produce, baseline quality |
| **AWQ** | scales and clips weights **before** quantising |
| **DWQ** | **fine-tunes the quantisation itself** — including scales and biases — using the **unquantised model as a teacher** |

**The result that matters:**

> **A 4-bit DWQ model reaches the quality of a 6-bit or even 8-bit model quantised the standard way.**

**Work out what that means for your 18 GB budget.** A 27B at standard 4-bit costs ~16.8 GB and leaves
almost nothing for cache. The same model at **4-bit DWQ costs the same ~16.8 GB but behaves like the
6-bit build**, which would otherwise need ~22.9 GB — **more than you have.**

**DWQ does not make the model smaller. It makes the bits you already spent worth more.** It is the
only technique in this document that improves quality *without* costing memory, and it is
Apple-Silicon-native.

**The catch:** DWQ takes meaningfully longer to *produce* than dynamic quantisation, because it is a
short training run against a teacher. You pay once, offline, then run the result forever. With an
8 TB SSD you can keep every variant you build.

```bash
# knobs that matter
--target-bpw <n>     # default parameter set reaches roughly 4.5–5.5 BPW
--group-size 32      # smaller group = finer quantisation parameters, slightly larger file
```

**Reference point for expectations:** standard Q4 costs about **1–3% perplexity** against FP16. DWQ
is aimed squarely at recovering that.

**Action: prefer a DWQ or AWQ build over a plain 4-bit build whenever one exists for your model.**
Check the model's MLX community page before settling for `dynamic_quant`.

### 5d. What NOT to spend time on — the Neural Engine

A recurring dead end, settled here so it is not re-investigated.

**Do not try to run your LLM on the Apple Neural Engine.**

> *"The ANE is a **fixed shape accelerator** built for CoreML, and **autoregressive decode is the one
> workload it handles badly**... It was designed for convolutions, not text generation."*

And the decisive empirical point:

> *"Every serious local LLM runtime — **llama.cpp, MLX, Ollama, LM Studio** — put the whole model on
> the GPU and **never touch the ANE**."*

When every runtime independently ignores a piece of silicon for this workload, that is a settled
result, not an oversight. The ANE is genuinely extraordinary at **~6.6 TFLOPS/watt — roughly 80×
the efficiency per operation of an A100** — and remains the right target for small always-on models
in power-constrained settings. **It is the wrong target for generating tokens from a 27B.**

**Related, and worth knowing before any upgrade decision:** the **M5's "Neural Accelerators" are a
different thing entirely** — matrix units built *inside the GPU pipeline*, not the ANE. Apple's own
MLX benchmarks put them at **3.3–4× faster time-to-first-token than M4** and **19–27% faster token
generation**. That, not the ANE, is what a future Mac would actually buy you.

## 6. What to actually do next, in order

0. **Check and raise `iogpu.wired_limit_mb` first** (§5b) — it governs how much of your 24 GB
   Metal may use at all, and every budget in this file sits under it.
1. **Install MLX / mlx-lm and make it your default.** Biggest single win available to you, costs
   nothing. ([mlx-lm](https://github.com/ml-explore/mlx-lm))
2. **Use a DWQ or AWQ build, not a plain 4-bit one** (§5c). Free quality — a 4-bit DWQ model
   performs like a 6–8-bit standard build at the same file size. Check the model's MLX community
   page before settling for `dynamic_quant`.
3. **Set up prefix caching** before chasing any decoding trick. Free, and it compounds every turn.
4. **Test speculative decoding under MLX** — not llama.cpp. Measure; do not trust the 70 tok/s figures.
5. **Quantise your KV cache by default.** ~50% off the one term that grows without bound.
6. **Build the Tier 3 rig once**, since you have the 8 TB. ~1.7 TB, one-time, then a very large model
   is permanently available for overnight work.
7. **Watch [mlx-lm #1438](https://github.com/ml-explore/mlx-lm/issues/1438).** If MLX ships expert
   streaming, your 8 TB SSD becomes usable for *fast* huge-model inference rather than slow — that
   would be the biggest single change to this document.
8. **Send me the Turbo Fieldfare link** and I will fill that gap.
9. **Do not experiment with the Neural Engine** (§5d) — settled dead end for token generation.
10. **When you outgrow one box, add a second Mac over Thunderbolt 5** (§7), not a bigger quantisation
    compromise. That is the only remaining lever.

---

---

## 7. Breaking the 24 GB ceiling — the only way past it

Everything above optimises **inside** one machine. This section is the honest answer to *"get it to
the peak that can't be evolved any more."*

**On a single 24 GB Mac mini, the peak is now defined.** Weights + KV cache + drafter must fit in
~18–19 GB (raisable via §5b). DWQ (§5c) makes those bits count for more. Layer streaming and expert
streaming (`kimik3 hwmini.md`) trade time for space at seconds per token. **There is no further
single-box lever that is not already in this document.**

**Past that, you do not optimise. You add machines.**

### Distributed inference across Apple Silicon

| Property | Detail |
|---|---|
| Tooling | **EXO / `exo-distributed`**, and **MLX Distributed** |
| Discovery | **zero-configuration** — auto peer discovery and master election |
| Interconnect | **RDMA over Thunderbolt 5** — direct memory access, low latency |
| Backend | **MLX** — native Apple Silicon, so §5c's DWQ builds still apply |
| Parallelism | **both pipeline and tensor parallelism** |
| Reported reach | **2–4 Macs → models of 200B+ parameters** |

Concretely, reported as runnable across a small cluster: **MiniMax M2.5 (173 GB)** and **Llama 3.3
70B** — models that cannot be loaded on any single 24 GB machine at any quantisation.

**Thunderbolt is the whole trick.** EXO works over ordinary networking, but *"Thunderbolt provides
significantly lower latency"*, and TB5 RDMA is what makes tensor parallelism viable rather than
merely possible. **Interconnect bandwidth is the binding constraint on a distributed setup, exactly
as memory bandwidth is on a single one.**

### What this means for your ceiling

| Configuration | Realistic reach |
|---|---|
| **1 × M4 24 GB** (you now) | ~27B at 4-bit DWQ, or 35B MoE at ~8 GB, interactive |
| **1 × M4 + 8 TB SSD, streaming** | 2.78T at ~25 s/token (`kimik3 hwmini.md`) — not interactive |
| **2 × Mac over TB5** | roughly double the resident budget — 70B class becomes reachable |
| **4 × Mac over TB5** | **200B+**, per EXO's reported range |

**So the true ceiling is not a setting — it is a purchase.** Everything cheaper than a second machine
is already written down in this file.

---

## 8. Sustained operation — the part benchmarks hide

A configuration that works for 60 seconds and fails at 10 minutes is not a working configuration.

**Your form factor is on the right side of this.** The Mac mini has **active cooling and sustains
full performance indefinitely**, unlike fanless Macs. But:

> *"Fan noise is a signal that **sustained all-core prefetch plus large batches can throttle sooner
> than short burst benchmarks suggest**."*

**The acceptance test, adopt it verbatim:**

> ***"Treat 10-minute steady runs as the acceptance test, not a 60-second leaderboard screenshot."***

That belongs in Step 5 of the workflow. A dry-run load test that passes instantly can still fail
under a real agentic session.

### Memory pressure is your real gauge

**Watch Activity Monitor's memory pressure while tokens stream.** Elevated pressure means you are
**past the knee of the curve** — and the fix is not to push through it:

1. drop one quantisation tier, or
2. shrink context, or
3. reduce parallel sessions

**Swap is the failure mode to fear, not slowness.** Reference point: on a 16 GB machine, exceeding
the ceiling drops output **below 5 tok/s** once it swaps. Your **24 GB is described as the
professional requirement to avoid "swap-death"** — you are above the line, but only if you keep the
rest of the machine quiet.

### Housekeeping that is not optional at this margin

> *"Close heavy browsers, pause cloud sync, and avoid concurrent indexing — **on large models, small
> background churn is enough to tip you into swap**."*

At Tier 2 (§3) you are running with 1–2 GB of headroom. A Spotlight reindex or an iCloud sync is
enough to cross it. **Treat background quiet as part of the configuration, not as hygiene.**

---

## 9. Honest gaps

- **Nothing here was run on your machine.** Every number is someone else's measurement on similar
  hardware. Your M4 (10-core GPU) is **not** the M4 **Pro** used in the MLX-vs-Ollama benchmark —
  expect lower absolute numbers than the 130 tok/s figure.
- **The ~18 GB Metal ceiling is extrapolated** from a 16 GB machine's observed 12.71 GB (≈79%). It is
  an estimate; your startup log has the real value.
- **KTransformers Metal support is suspect.** The claim came from a low-quality blog that also said
  the Metal backend *"offloads matrix multiplications to the Apple Neural Engine"* — Metal and the
  ANE are different hardware paths, so that sentence is confused. **Verify against the repo before
  relying on it.**
- **Most Layer-2 KV methods are research implementations**, not packaged tools. `KVCache-Factory` is
  the practical entry point for comparing them.
- **The "MLX degrades past 40K context" claim is single-source.** Benchmark it rather than trusting it.
- **DFlash 2 was not tested on Apple Silicon here.** The reasoning that it should work under MLX and
  not under llama.cpp is an inference from the *general* Metal speculative-decoding result, not a
  DFlash-2-specific measurement.
- **Turbo Fieldfare: unresolved.** See the box in section 2.
- **This landscape moves in weeks.** llama.cpp's speculative implementation is under active
  development, with expectations it *"will close most of the gap by Q4 2026"* — which would partly
  invalidate this file's central recommendation. Re-check if this is more than a month old.

---

## Sources

1. [MLX vs llama.cpp on Apple Silicon: Benchmarks, M5 Neural Accelerators, and Why Ollama Switched](https://yage.ai/share/mlx-apple-silicon-en-20260331.html) — 130 vs 43 tok/s; Ollama's 58→112 switch
2. [MLX vs llama.cpp — 2026 Benchmark Comparison](https://www.compute-market.com/blog/mlx-vs-llama-cpp-apple-silicon-2026) — 20–87% under 14B; convergence above 27B
3. [Apple's MLX Runs Local LLMs 3x Faster Than llama.cpp — Until Your Context Hits 40K](https://pub.towardsai.net/apples-mlx-runs-local-llms-3x-faster-than-llama-cpp-until-your-context-hits-40k-715ec441afbb) — the 40K caveat
4. [MTP speculative decoding degrades throughput on Metal — llama.cpp issue #23752](https://github.com/ggml-org/llama.cpp/issues/23752) — **−11% to −28%**, kernel-dispatch cause, MLX fusion contrast, Recurrent Drafter 2.3×
5. [MoE expert streaming / SSD offload for Apple Silicon — mlx-lm issue #1438](https://github.com/ml-explore/mlx-lm/issues/1438) — **open feature request**
6. [TurboQuant — 0xSero/turboquant](https://github.com/0xSero/turboquant) — 3-bit keys / 2-bit values, Triton + vLLM, ICLR 2026
7. [What is TurboQuant and why it matters — LMCache blog](https://blog.lmcache.ai/en/2026/04/15/what-is-turboquant-and-why-it-matters-for-llm-inference-in-laymens-term/) — two-stage rewrite, 4× context
8. [TurboQuant Explained — Vast.ai](https://vast.ai/article/turboquant-explained-llm-memory-inference) — 5× memory reduction framing
9. [Fast-TurboQuant: multiplier-free online vector quantization — arXiv 2606.21448](https://arxiv.org/pdf/2606.21448)
10. [KVCache-Factory](https://github.com/Zefan-Cai/KVCache-Factory) — unified KV compression playground
11. [PyramidKV — arXiv 2406.02069](https://arxiv.org/pdf/2406.02069) — beats H2O/SnapKV/StreamingLLM at small caches
12. [xKV: Cross-Layer KV-Cache Compression — arXiv 2503.18893](https://arxiv.org/pdf/2503.18893) — 89.22% avg, +1.7% over KIVI-2
13. [KV Cache Compression and Its Infra Problems — NVIDIA Efficient AI](https://research.nvidia.com/labs/eai/blogs/kv-cache-compression-and-its-infra-problems/)
14. [LLM Quantization Guide: GGUF vs AWQ vs GPTQ vs bitsandbytes (2026)](https://www.premai.io/blog/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026/) — Q4_K_M 92% retention; AWQ 741 tok/s; bitsandbytes-only QLoRA
15. [QuIP# — arXiv 2402.04396](https://arxiv.org/pdf/2402.04396)
16. [Resource-Efficient Language Models: Quantization — arXiv 2505.08620](https://arxiv.org/pdf/2505.08620) — the ≥4-bit parity finding
17. [KTransformers](https://github.com/kvcache-ai/ktransformers) — hybrid CPU/GPU MoE
18. [KTransformers: running a 671B MoE on a single GPU — noze](https://www.noze.it/en/insights/ktransformers-hybrid-cpu-gpu-inference/) — v0.6.3 model support
19. [FlashMoE: ML-Based Cache Replacement for MoE on Edge — arXiv 2601.17063](https://arxiv.org/abs/2601.17063)
20. [HOBBIT: Mixed Precision Expert Offloading — arXiv 2411.01433](https://arxiv.org/pdf/2411.01433)
21. [PIPO: Pipelined Offloading for Consumer Devices — arXiv 2504.03664](https://arxiv.org/pdf/2504.03664)
22. [Efficient MoE LLM Inference with Apple Silicon NPUs (NPUMoE) — arXiv 2604.18788](https://arxiv.org/html/2604.18788v1)
23. [`FareedKhan-dev/kimi-k3-in-c`](https://github.com/FareedKhan-dev/kimi-k3-in-c) — 2.78T in 8.24 GB, macOS/arm64
24. [Performant local MoE CPU inference with GPU acceleration in llama.cpp — HF blog](https://huggingface.co/blog/Doctor-Shotgun/llamacpp-moe-offload-guide)
25. [llama.cpp discussion #21112 — Optimize my llama.cpp](https://github.com/ggml-org/llama.cpp/discussions/21112) — `--no-mmap` 98%→71%; context-before-offload tuning order
26. [Insufficient documentation for `-ot` — llama.cpp discussion #13154](https://github.com/ggml-org/llama.cpp/discussions/13154)
27. [`--load-mode` refactor — llama.cpp issue #26110](https://github.com/ggml-org/llama.cpp/issues/26110) — load-mode precedence
28. [ofox.ai — Qwen 3.8 27B run locally](https://ofox.ai/blog/qwen-3-8-27b-run-locally-vram-gguf-2026/) — quant ladder, KV cache table, `res = -3`, Metal ceiling
29. [Tune llama.cpp on Apple Silicon: 7 Flags](https://medium.com/@michael.hannecke/tuning-llama-cpp-on-apple-silicon-843f37a6c3dc) ⚠️ **blocks automated probes** — returns no response to `curl` even with browser headers, but the article was **confirmed live and its content retrieved via search on 2026-09-02**. The link is correct; only direct fetching is blocked.
30. [mlx-lm `LEARNED_QUANTS.md`](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LEARNED_QUANTS.md) — **primary**: DWQ/AWQ/dynamic_quant, `--target-bpw`, `--group-size`
31. [MLX Quantization on Apple Silicon: dynamic_quant vs AWQ vs GPTQ vs DWQ — M. Hannecke](https://medium.com/@michael.hannecke/mlx-quantization-on-apple-silicon-dynamic-quant-vs-awq-vs-gptq-vs-dwq-8b2a5af2b53f) — the 4-bit-DWQ-equals-6/8-bit result
32. [Local LLM Quantization Quality Benchmarks 2026 — Presenc AI](https://presenc.ai/research/local-llm-quantization-quality-benchmarks-2026) — Q4 costs 1–3% perplexity vs FP16
33. [Apple Neural Engine for LLM Inference: What Actually Works — InsiderLLM](https://insiderllm.com/guides/apple-neural-engine-llm-inference/) — why the ANE is wrong for autoregressive decode
34. [GPU vs Apple Neural Engine for Local LLM Inference — Contra Collective](https://contracollective.com/blog/gpu-vs-apple-neural-engine-local-llm-inference-m5-max-2026) — every runtime ignores the ANE; M5 Neural Accelerators are a different thing
35. [Model Sharding With EXO: Run Larger LLMs Across Macs](https://tokenbyte.co/model-sharding-with-exo-how-to-link-macs-and-run-models-bigger-than-any-one-of-them/) — distributed inference
36. [exo-distributed](https://lobehub.com/skills/plurigrid-asi-exo-distributed) — RDMA over Thunderbolt 5, pipeline + tensor parallelism, MLX backend
37. [Connecting Multiple M4 Mac Minis to Run LLMs — Ithy](https://ithy.com/article/connect-m4-mac-minis-for-llm-79zt67ll) — 2–4 Macs, 200B+ range
38. [2026 Mac M4 Local LLM Inference: llama.cpp vs Ollama Matrix — LlmMac](https://llmmac.com/blog/articles/2026-mac-m4-llamacpp-ollama-inference-matrix.html) — thermals, memory pressure, the 10-minute acceptance test
39. [Best LLMs for Mac Mini M4 24GB RAM — modelfit](https://modelfit.io/blog/best-llm-mac-mini-m4-24gb/) — 24 GB as the swap-death threshold
40. [Tuning llama-server on Apple Silicon — M. Hannecke](https://medium.com/@michael.hannecke/tuning-llama-server-on-apple-silicon-9b3e778ab100) — companion piece, recovered on the 2026-09-02 re-sweep
41. [Llama.cpp vs MLX on Apple Silicon — M. Hannecke](https://medium.com/@michael.hannecke/llama-cpp-vs-mlx-on-apple-mx-775ee59df0ee) — direct comparison, recovered on the re-sweep
42. [apple-silicon-llm-bench](https://github.com/john-rocky/apple-silicon-llm-bench) — reproducible Apple Silicon benchmark harness

**Companion files in this folder:** `qwen38-27b hwmini.md` · `kimik3 hwmini.md` · `mach1 hwmini.md` · `dflash2 hwmini.md`

## Change Log

- **2026-09-01** — Created `UHWmini.md`. Scope was **confirmed with the user before researching**
  rather than guessed: **three tiers (Daily / Heavy / Ceiling) × all four workloads** (agentic
  coding, long-doc/RAG, chat, vision), targeting a **Mac mini M4, 24 GB unified, 8 TB SSD**.
  Verified the user's five named tools — **llama.cpp ✓**, **TurboQuant ✓** (ICLR 2026, 3-bit keys /
  2-bit values, Triton + vLLM), **Turbovec ✓** (TurboQuant-compatible vector search + graph memory
  for constrained RAG), **KIVI ✓** — and **could not find "Turbo Fieldfare" in any reachable
  source**, recorded as an open question rather than filled with a guess.
  Added ~25 further tools across five layers (weight quantisation, KV-cache compression,
  offload/streaming, decoding/pace, retrieval), each with an explicit **Mac-compatibility** column.
  **Principal finding, which reorganised the whole document: most of this tooling is CUDA-path and
  does not apply to this machine — and one technique inverts on Apple Silicon.** Speculative decoding
  in llama.cpp on Metal is a measured **net loss (−11% even at 100% draft acceptance, −28% at
  n_max=6)** because each draft-verify step launches a separate Metal kernel whose dispatch cost
  exceeds the speculation saving; **MLX fuses verification into one compute graph and the same idea
  becomes a large win** (Apple's Recurrent Drafter: 2.3× on Metal). This directly answers the user's
  DFlash 2 question — **pursue it through MLX, not llama.cpp**, where it would most likely make
  things slower.
  **Second structural finding: MoE expert streaming from SSD is not shipped in MLX** — it is open
  feature request `ml-explore/mlx-lm#1438` — so the user's 8 TB SSD is the right hardware for an idea
  whose Apple-side software does not yet exist. The one project doing it today on macOS/arm64 is
  `kimi-k3-in-c`, which becomes the Ceiling tier: **2.78T parameters, ~1.7 TB of disk, ~24–26
  s/token estimated at 24 GB**, with byte-identical output across memory configurations so that
  memory dial costs zero quality.
  Budgeting is done against **~18 GB practically addressable by Metal**, extrapolated from a 16 GB
  Mac's observed 12.71 GB ceiling (~79%) and flagged as an estimate to be replaced by the user's own
  `recommendedMaxWorkingSetSize`. Recorded the hard failure mode — 4-bit 27B on 16 GB dies with
  `res = -3` rather than degrading — and that at 24 GB it fits with only 1–2 GB of margin.
  Included an 8-step workflow with an explicit loop-back at the dry-run load test, the tuning-order
  rule (**tune offload at small context, then grow context, never the reverse**), and a
  speed-optimisation order putting **free prefix caching before any decoding trick**.
  Flagged honestly: nothing was run on the user's machine; the MLX benchmark hardware was an **M4
  Pro**, not their M4; the **KTransformers Metal claim is suspect** (its source confuses Metal with
  the ANE); the "MLX degrades past 40K context" claim is single-source; the DFlash-2-on-MLX
  recommendation is an inference from the general Metal result rather than a DFlash-2-specific
  measurement; and llama.cpp's speculative work is expected to *"close most of the gap by Q4 2026"*,
  which would partly invalidate the central recommendation.

- **2026-09-02 (re-sweep fix)** — Corrected an error introduced by the previous sweep: three source
  links had been flagged as possibly "gone" when all three are **live and their content retrievable**
  — they merely block automated `curl` probes. Flags rewritten to say so accurately.
  Re-reading one of them (*Tune llama.cpp on Apple Silicon: 7 Flags*) surfaced a **substantive gap in
  this document** and section 5b was added: **`sudo sysctl iogpu.wired_limit_mb=N`**, described by that
  source as *"the single most important tuning step"* and **not a llama.cpp flag at all**. This changes
  section 1 — the ~18–19 GB Metal ceiling is a **default, not a hardware limit**, and is raisable, which
  on a 24 GB machine is the difference between a 4-bit 27B fitting and crashing with `res = -3`. The
  memory table and the section 6 action list were updated to put this first, with a caution to raise it
  in steps and keep headroom rather than maxing it. Also added the seven Apple-Silicon flags that
  actually matter (`-ngl 99 -fa 1 -c -b 2048 -ub 2048 --cache-type-k/v q8_0`, plus `--mlock --prio 2`
  with headroom) and the source's warning that **most tutorial flags are copied from x86 server docs and
  have no effect on M-series chips**.

- **2026-09-02 (peak pass)** — Deep-research pass to push this file to the ceiling, at the user's
  direction that it is the most important file in the folder. Four additions, one of which changes
  what the machine can run.
  **§5c — DWQ, the largest single win available.** MLX ships **learned quantization** that GGUF
  pipelines do not: `dynamic_quant`, **AWQ** (scales and clips before quantising) and **DWQ**, which
  fine-tunes the quantisation itself — scales and biases included — **against the unquantised model as
  a teacher**. The consequence is that **a 4-bit DWQ model reaches the quality of a 6-bit or 8-bit
  standard build**. Worked through for this machine: a 27B at 4-bit DWQ occupies the same ~16.8 GB but
  behaves like the 6-bit build that would need ~22.9 GB — **more memory than the machine has**. It is
  the only technique in this file that raises quality **without** costing memory. Recorded the knobs
  (`--target-bpw`, default range ≈4.5–5.5 BPW; `--group-size 32`), the cost (a one-off offline
  training run), and the baseline it recovers (standard Q4 costs **1–3% perplexity** vs FP16).
  **§5d — the Neural Engine is a settled dead end**, recorded so it is not re-investigated: the ANE is
  a *"fixed shape accelerator"* whose worst workload is autoregressive decode, and **llama.cpp, MLX,
  Ollama and LM Studio all independently ignore it** for LLMs. Noted it remains extraordinary on
  efficiency (**~6.6 TFLOPS/watt, ~80× an A100 per operation**) for small always-on models, and that
  the **M5's "Neural Accelerators" are a different thing** — matrix units inside the GPU pipeline,
  benchmarked by Apple at **3.3–4× faster time-to-first-token and 19–27% faster generation than M4** —
  which is what an upgrade would actually buy.
  **§7 — the real ceiling, and the only way past it.** Stated plainly that after §5b, §5c and the
  streaming tiers there is **no further single-box lever left in this document**, and that past that
  point you add machines rather than settings: **EXO / `exo-distributed` and MLX Distributed**, with
  **zero-config peer discovery**, **RDMA over Thunderbolt 5**, an **MLX backend** (so DWQ builds still
  apply) and **both pipeline and tensor parallelism**, reaching **200B+ across 2–4 Macs** —
  MiniMax M2.5 (173 GB) and Llama 3.3 70B are cited as runnable that way. Added a reach table making
  the conclusion explicit: **the true ceiling is a purchase, not a setting.**
  **§8 — sustained operation**, the failure mode benchmarks hide. The mini's **active cooling sustains
  full performance indefinitely**, but sustained all-core work throttles sooner than burst benchmarks
  suggest. Adopted the acceptance rule verbatim — ***"treat 10-minute steady runs as the acceptance
  test, not a 60-second leaderboard screenshot"*** — and wired it into workflow Step 5. Recorded
  **memory pressure in Activity Monitor as the real gauge** (elevated = past the knee; drop a quant
  tier, shrink context, or cut parallel sessions), that **swap, not slowness, is the failure to fear**
  (a 16 GB machine falls below 5 tok/s once it swaps), that **24 GB is the stated professional
  threshold to avoid "swap-death"**, and that at Tier 2's 1–2 GB of headroom **background churn — a
  Spotlight reindex, an iCloud sync — is enough to tip the machine into swap**, making background
  quiet part of the configuration rather than hygiene.
  Renumbered sections to stay continuous, extended the action list to 10 items (DWQ promoted to #2,
  ANE marked as a non-action, adding a second Mac as the final lever), and added **13 sources**.