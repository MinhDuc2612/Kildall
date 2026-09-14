# finetune&train — Soup: fine-tuning an 8B model on a 4 GB GPU

**Built:** 2026-09-02 · Sample 2 · self-contained
**Source watched:** [instagram.com/reel/Db-5SSwJHls](https://www.instagram.com/reel/Db-5SSwJHls/) —
**100xEngineers**, 2026-08-13. Downloaded and transcribed locally with `whisper.cpp` (no captions),
28 frames extracted.

> **Verdict up front: the reel is accurate.** Every number it gives checks out against the project's
> own measurements — 3.3 GB, 119 tok/s, 4 GB laptop GPU, Apache-2.0, Kazakhstan. That is rare in this
> folder. The project is also **more rigorous and more self-critical than the reel conveys**, and the
> genuinely interesting material is in what the reel left out.

## ⚡ ANSWER FIRST

**What this is:** Soup — `MakazhanAlpamys/Soup`, **Apache-2.0, 4,577 stars**.
Fine-tune an **8B model on a 4 GB GPU**, from one YAML file.

| | |
|---|---|
| Memory | **3.32 GB peak** for an 8B model |
| Speed | **119.6 tok/s** on an RTX 3050 |
| Trick | **layer streaming** — frozen layers stay in RAM, one goes to VRAM at a time |

⚠️ **Runs on your Mac? Yes, but the numbers do not transfer.** Those figures are **CUDA/NF4**. The
author lists **Apple Silicon as unvalidated, hardware-gated work**. Python **3.13+ unsupported**.

**Why trust it anyway:** they publish their own worst bugs — including a **silent wrong-gradient
defect** where the loss curve looked healthy while training was broken.

**For Orbi: use Unsloth instead** — native macOS app and MLX support.

---

---

## 1. Verified facts

Live GitHub API, 2026-09-02:

| Field | Value |
|---|---|
| Repo | [`MakazhanAlpamys/Soup`](https://github.com/MakazhanAlpamys/Soup) |
| Description | *"Fine-tune LLMs from one YAML. Layer streaming trains an 8B model on a 4 GB laptop GPU."* |
| Author | **Alpamys Makazhan**, Almaty, **Kazakhstan** ✅ *(reel's "alpami smakajan" is a mis-hearing)* |
| Legal entity | **MePlay, Inc.** — the name that appears on checkout, not "Soup" |
| Licence | **Apache-2.0** ✅ |
| Stars / forks | **4,577 / 677** |
| Open issues | 51 |
| Language | Python |
| Created | 2026-02-20 |
| Last push | **2026-09-01** — actively developed |
| Package | [`soup-cli` on PyPI](https://pypi.org/project/soup-cli/) · Website [trysoup.dev](https://trysoup.dev) |

**Reel claim check — all pass:**

| Reel said | Verified |
|---|---|
| 8B normally needs ~16 GB VRAM | ✅ consistent — README requires **8 GB+ for 7B with QLoRA** |
| Soup gets it to **3.3 GB** | ✅ **3.32 GB peak**, measured |
| **119 tokens/sec** on a 4 GB laptop GPU | ✅ **119.6 tok/s**, RTX 3050 Laptop 4 GB, Llama-3.1-8B-Instruct + NF4 |
| One YAML + one command | ✅ `soup train` |
| Open source | ✅ Apache-2.0 |

⚠️ **One imprecision:** the reel says *"a solo founder."* It is maintained in the open by one person,
but there is a **registered company, MePlay, Inc.**, behind it. Not a garage project.

---

## 2. What layer streaming actually does

The mechanism, in the project's own framing: decoder layers of the base model **that do not change
during training** are held in **main memory**, and only the layer currently being computed is sent to
**VRAM**, one at a time.

**Why this works at all:** in LoRA/QLoRA fine-tuning the base weights are *frozen*. They are needed for
the forward and backward pass but never updated. So they do not have to be resident — only *present at
the moment they are used*. Layer streaming turns a **capacity** problem into a **bandwidth** problem.

**And bandwidth turns out not to be the bottleneck.** From the project's own profiling:

| Measured cost | Share of step |
|---|---|
| Host-to-device byte transfer | **1.4%** |
| Compute stream waiting on a copy | **0.20%** |
| Per-layer **NF4 dequantisation** | **9.8%** — the largest streaming-specific cost |
| Step throughput vs same-session GEMM ceiling | **71.3%** |

**The copy is essentially free; the dequantisation is what costs you.** That is a genuinely
counter-intuitive result and it is the technical heart of the project.

### The result that sounds impossible

> **"Replication on hardware nothing like the original: 119.6 tok/s on the RTX 3050 against a median
> 113.00 on an H100, at the same 3.32 GB peak."**

**A 4 GB laptop GPU matching — slightly beating — an H100 on this workload.** Read it correctly: this
is not "a 3050 is faster than an H100." It means **the workload is not compute-bound**, so the H100's
advantage has nothing to bite on, and both machines hit the same constraint. The README says exactly
that: *"the constraint is common to both machines and is not the GPU's compute."*

---

## 3. What the reel left out — the engineering honesty

This is the part worth your attention, and none of it is in the video.

**1. They found a silent wrong-gradient bug in their own method and published it.**
> *"On NF4 above ~165 MiB per layer the forward stayed **bit-exact** and the **loss curve looked
> healthy** while the **gradients were wrong**."*

A forward pass that is bit-exact and a loss curve that looks fine, while training is quietly broken.
That is close to the worst failure mode in machine learning — **it does not look like a failure**. The
cause was traced to an upstream library, **reported there**, and the repair gated against controls on
real 32B and 72B models.

**2. They publish the benchmark that makes them look bad.**
> *"A comparison against DeepSpeed — **including the result that does not flatter us**: eight cards of
> ZeRO-3 are slower than one card training resident."*

**3. Correctness is verified at real scale, not on toys.**
> *"Bit-exactness at real model sizes instead of three-layer toys: forward from **0.5B to 72B**,
> backward at **8B and 14B**."*
> *"Trained-model quality, measured for the first time, and **indistinguishable from a resident run**."*

That last one is the claim that matters most. Memory savings are worthless if the resulting model is
worse. They measured it.

**4. Bugs are described by how they were found.**
One entry notes a label-mask defect where the mask was built from a mapping's **key strings** — *"No
exception, no warning, a loss curve that looks like training. **Found by reading the type, not by
hitting the bug.**"*

**A project that documents its own silent-failure bugs in the README is behaving better than most
funded labs.** Treat that as the strongest quality signal here — stronger than the star count.

---

## 4. Can you run it on your Mac mini M4? — yes, with caveats

This is the question that matters given `../UHWmini.md`.

| Requirement | Your machine |
|---|---|
| **Apple Silicon (MPS)** — explicitly supported | ✅ M4 |
| Python **3.10 / 3.11 / 3.12** (3.13+ **not** supported — PyTorch stack unvalidated) | ⚠️ check your version |
| 8 GB+ VRAM for 7B with QLoRA | ✅ 24 GB unified |
| CUDA | ❌ — recommended, not required |

Support tiers, verbatim: *"GPU with CUDA (**recommended**), Apple Silicon (**MPS**), or CPU
(**experimental — very slow**)."* There is also an **`mlx` optional extra**, alongside `train`, `fast`
(unsloth, 2–5× faster), `vision`, `qat`, `serve`, `eval`, `deepspeed`, `liger`, `onnx`, `tensorrt`.

### ⚠️ Two Apple-Silicon-specific things to know

**1. There *was* a serious Apple Silicon bug. It is fixed — do not read it as current.**
> *"On Apple Silicon, `quantization: 4bit` was silently rewritten to `none`. `detect_device()` did not
> know MLX, so every run reported 'CPU (no GPU detected)' and quietly downgraded."*

This appears in the **list of defects found and repaired** — *"the quantization decision is now
explicit and testable instead of hidden inside a 900-line function."* But it tells you the shape of
the risk: **Apple Silicon has historically been the under-tested path**, and the failure mode was
silent downgrade rather than an error.

**2. Apple Silicon is still explicitly hardware-gated work.**
> *"Donations buy GPU time for the hardware-gated work — **multi-GPU, 8B+ validation, Apple Silicon** —
> that a single 4 GB laptop cannot reach."*

**The author says outright that Apple Silicon is not fully validated**, and ships such features *"behind
honest 'requires \<hardware\>' gates rather than unverified claims."*

**Practical guidance:** the headline **3.32 GB / 119.6 tok/s is an NF4 CUDA result and should not be
assumed to transfer to your M4.** Run `soup doctor` first, confirm the device is detected as MPS and
not "CPU (no GPU detected)", and **verify your quantisation setting was actually honoured rather than
silently downgraded** before trusting any memory figure.

---

## 5. Install and use

```bash
pip install soup-cli              # light: CLI, config, data tools — no PyTorch
pip install "soup-cli[train]"     # + torch, transformers, peft, trl, datasets
pip install "soup-cli[all]"       # everything
pip install "soup-cli[fast]"      # unsloth backend, 2–5× faster
```

Then `soup init`, `soup data …`, `soup train`. The light install is enough for config and data work
without pulling PyTorch — a sensible split.

**Docker:** an image is published to **GHCR on every release**, so you can *"run Soup without
installing CUDA or PyTorch locally."* On a Mac that is often the cleaner path than fighting wheels.

**Methods supported:** **SFT, DPO, GRPO, KTO**, plus eval, gating, adapter arithmetic and export. The
reel only mentions fine-tuning; the preference-optimisation methods (DPO/GRPO/KTO) are the more
capable half.

---

## 6. Where this fits with the rest of this folder

`../UHWmini.md` covers **running** models in constrained memory. Soup is the **training** counterpart, and
the two use the same core idea from opposite ends:

| | `../kimik3 hwmini.md` (inference) | **Soup (training)** |
|---|---|---|
| Trick | stream **experts** from disk, never resident | stream **layers** from RAM, one at a time |
| Why it works | MoE sparsity — only ~4% fires per token | frozen base weights — needed, never updated |
| Turns | capacity → **disk bandwidth** | capacity → **host-device bandwidth** |
| Cost | severe — **seconds per token** | **near-zero — copy is 1.4% of the step** |

**The contrast is the lesson.** Streaming from **disk** is punishing; streaming from **main memory**
is almost free. Soup's result is strong because PCIe/unified-memory bandwidth is fast enough that the
transfer disappears into the compute — which is why the H100 comparison lands the way it does.

---

## 7. Honest gaps

- **Not installed, not run, nothing reproduced.** Every figure is the project's own measurement.
- **The independent reproduction was not evaluated.** [`griffinstalha/soup-4gb-layer-streaming-reproduction`](https://github.com/griffinstalha/soup-4gb-layer-streaming-reproduction)
  exists (created 2026-08-29, **0 stars**, no licence) but its results were not read. It is the obvious
  next check, since everything above is single-party.
- **The reel's "went viral on Hacker News" was not verified** — no HN thread was located.
- **The H100 comparison is the project's own replication**, not third-party.
- **Apple Silicon performance is unmeasured here**, by anyone — including the author, who says so.
- **README-level reading only.** The benchmark records under `benchmarks/` were not opened.

## 8. Sources

1. [`MakazhanAlpamys/Soup`](https://github.com/MakazhanAlpamys/Soup) — primary: README and live GitHub API metadata, 2026-09-02
2. [`soup-cli` on PyPI](https://pypi.org/project/soup-cli/)
3. [trysoup.dev](https://trysoup.dev) — project site
4. [Soup CLI on Product Hunt](https://www.producthunt.com/products/soup-cli)
5. [GIGAZINE — 'Soup' fine-tunes an 8B model on a 4 GB laptop GPU](https://gigazine.net/gsc_news/en/20260806-soup-fine-tune-llm/) — the layer-streaming description and RTX 3050 figures
6. [Soup: Fine-Tune an 8B Model on a 4 GB GPU — Luca Berton](https://lucaberton.com/blog/soup-cli-fine-tuning-llm-layer-streaming/)
7. [`griffinstalha/soup-4gb-layer-streaming-reproduction`](https://github.com/griffinstalha/soup-4gb-layer-streaming-reproduction) — independent reproduction, **not evaluated here**
8. Reel — [instagram.com/reel/Db-5SSwJHls](https://www.instagram.com/reel/Db-5SSwJHls/), 100xEngineers, 2026-08-13

## Change Log

- **2026-09-02** — Created from one Instagram reel (100xEngineers, 2026-08-13), downloaded and
  **transcribed locally with `whisper.cpp`**. Subject verified as **`MakazhanAlpamys/Soup`** —
  **Apache-2.0, 4,577 stars, 677 forks, Python, pushed 2026-09-01**, by **Alpamys Makazhan** of Almaty,
  Kazakhstan, behind the registered entity **MePlay, Inc.**
  **Every numeric claim in the reel checks out**: 3.3 GB (**3.32 GB peak** measured), 119 tok/s
  (**119.6 tok/s**), on an **RTX 3050 Laptop 4 GB** running Llama-3.1-8B-Instruct with NF4, Apache-2.0,
  one YAML plus `soup train`. Recorded one imprecision — the reel's *"solo founder"* understates that a
  registered company stands behind it.
  Documented the mechanism the reel compresses: frozen base-model decoder layers are held in **main
  memory** and streamed to VRAM one at a time, which works because LoRA/QLoRA base weights are needed
  but never updated — converting a capacity problem into a bandwidth problem. Captured the project's
  own profiling showing **the bandwidth is not the bottleneck**: host-to-device transfer is **1.4%** of
  the step, the compute stream waits on a copy **0.20%** of the time, and the largest streaming-specific
  cost is **per-layer NF4 dequantisation at 9.8%**, with the step running at **71.3%** of the card's
  same-session GEMM ceiling. Recorded the striking replication — **119.6 tok/s on the RTX 3050 against
  a median 113.00 on an H100 at the same 3.32 GB peak** — with the correct reading that the workload is
  **not compute-bound**, which is the README's own explanation.
  Highlighted the engineering-honesty material the reel omits entirely: a **silent wrong-gradient
  defect** on NF4 above ~165 MiB per layer where *"the forward stayed bit-exact and the loss curve
  looked healthy while the gradients were wrong"*, traced to an upstream library and reported there;
  publication of **the DeepSpeed comparison that does not flatter them** (eight cards of ZeRO-3 slower
  than one card resident); **bit-exactness verified from 0.5B to 72B forward and 8B/14B backward**; and
  trained-model quality measured as **indistinguishable from a resident run**.
  Answered the Mac-specific question for the user's M4: **Apple Silicon (MPS) is explicitly supported**
  and 24 GB comfortably exceeds the 8 GB-for-7B-QLoRA requirement, but **Python 3.13+ is unsupported**,
  and two Apple-specific cautions apply — a **now-fixed** bug in which *"on Apple Silicon,
  `quantization: 4bit` was silently rewritten to `none`"* because `detect_device()` did not know MLX
  (recorded in past tense, as a repaired defect, not a current limitation), and the author's own
  statement that **Apple Silicon remains hardware-gated, unvalidated work**. Concluded that the
  headline 3.32 GB / 119.6 tok/s is a **CUDA NF4 result that should not be assumed to transfer**, and
  that `soup doctor` should be run first to confirm MPS detection and that quantisation was honoured
  rather than silently downgraded.
  Added a cross-reference contrasting Soup with `../kimik3 hwmini.md`: both stream to beat a capacity
  limit, but **streaming from disk costs seconds per token while streaming from main memory costs
  1.4% of a step** — the reason Soup's result is strong and Kimi-K3-in-C's is slow.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** block at the top, matching sample 1's
  presentation style: what the file is, the numbers that matter, and the decisive caveat, all before
  any discussion. No content changed; the research below now serves as backing detail.
