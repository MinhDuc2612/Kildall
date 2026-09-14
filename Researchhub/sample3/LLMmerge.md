# LLMmerge — Combining Models Across Families

**Built:** 2026-09-02 · Sample 3 · self-contained
**Question:** cross-family LLM merge methods — sparse upcycling, adapters, and everything adjacent.

> ## The headline: cross-family *weight merging* does not work, and the field says so
>
> > *"Current LLM merging methods are typically restricted to models with **same architecture and
> > compatible parameters**. However, **most open-source LLMs are heterogeneous**, rendering current
> > merging methods ineffective."*
>
> You cannot average Llama into Qwen. Different tokenizers, different hidden dimensions, different
> layer counts — the weights are not in the same space, so there is nothing meaningful to average.
>
> **Everything that genuinely works across families is not merging. It is knowledge transfer.** That
> distinction organises this entire file.

## ⚡ ANSWER FIRST

**The question:** can you merge models from different families?
**The answer: NO — and the field says so outright.**

> *"Current LLM merging methods are typically restricted to models with same architecture and
> compatible parameters... most open-source LLMs are heterogeneous, rendering current merging
> methods ineffective."*

**Three things get called "merging". Only one crosses families:**

| | Cross-family? | Cost |
|---|---|---|
| Weight merging (TIES, DARE) | ❌ same base only | free |
| Architectural surgery (upcycling) | ❌ one model | training |
| **Knowledge transfer (distillation)** | ✅ **the only real answer** | full training run |

**Most under-used answer: don't merge — ROUTE.** Two models behind a router give you both
capabilities today, zero training.

---

---

## The three things called "merging"

| | What it does | Cross-family? | Cost |
|---|---|---|---|
| **1. Weight merging** | arithmetic on weights of models sharing a base | ❌ **same family only** | free, no training |
| **2. Architectural surgery** | changes the model's shape — upcycling, frankenmerge | ❌ **one model at a time** | training compute |
| **3. Knowledge transfer** | teaches model B what model A knows | ✅ **the only real answer** | full training run |

**People asking for "cross-family merging" almost always want #3 and are told about #1.**

---

## 1. Weight merging — mature, free, and same-family only

All of these operate on **task vectors**: `task_vector = fine_tuned_weights − base_weights`. The delta
*is* the skill. Arithmetic on deltas is arithmetic on skills.

| Method | Mechanism |
|---|---|
| **Linear / Model Soup** | plain weighted average |
| **Task Arithmetic** | average task vectors. **Add** to gain a skill, **subtract** to suppress a behaviour |
| **SLERP** | spherical interpolation — respects weight-space geometry better than linear, two models at a time |
| **TIES-Merging** | resolves **sign conflicts**: when two task vectors disagree on a parameter's direction, naive addition cancels both. TIES trims and elects a sign first |
| **DARE** | preprocessing, not a merge method — **randomly drops up to 99% of task-vector weights**, then rescales the survivors. **Plugs into any of the above** |

**DARE's 99% number is the striking one.** You can discard almost the entire delta, rescale, and keep
the skill. It implies task vectors are **extremely redundant** — which is also why merging works at
all: there is room for several skills in the same weights without collision.

**Newer work:** **Activation-Informed Merging** (weights merged with awareness of activations, not
just parameters) · **CAMEx** (curvature-aware merging of experts) · **A Systematic Study of
In-the-Wild Model Merging** — the empirical survey of what actually holds up.

**Tooling: [mergekit](https://arxiv.org/pdf/2403.13257)** (Arcee) is the standard. Also `MergeLM`
(ICML 2024). **Hugging Face PEFT** ships merging natively.

**Hard constraint: all of these need a shared base model.** Two Llama-3 fine-tunes merge fine. Llama
and Qwen do not.

---

## 2. Architectural surgery — reshaping one model

### Sparse upcycling — dense → MoE

**The mechanism, precisely:** copy the MLP in each transformer block **E** times (E = expert count),
add a **learnable router** sending each token to the **top-k** experts.

**The detail that makes it work:** router initialisation is coordinated so the MoE **maintains
functional parity with the original dense function at startup**. You begin at the dense model's
quality and train from there, rather than from noise.

**Why it matters for hardware:** MoE memory tracks **active experts + dense trunk**, not total
parameters. Upcycling is therefore a way to **lower a dense model's memory floor** — see
`UHWmini.md` §6b, where this is recorded as the only build-time lever.

**2026 refinements:**

| Work | Contribution |
|---|---|
| **Drop-Upcycling** | partial **re-initialisation** of copied experts — pure copies are too correlated to specialise |
| **SPRI** | **SVD-partitioned residual initialisation** for data-constrained upcycling |
| **EMO** | progressive training of **extendable** MoE |
| **Continual LLM Upcycling** | predictor-gated bank-wise sparsity; demonstrated converting a Qwen2.5-8B dense model trained at 8K, continued at 32K |
| **Upcycling Instruction Tuning** | dense→MoE **via parameter merging** — the one place §1 and §2 meet |

> ### ⚠️ Upcycling is not lossless — and the failure hides
> *"Channel-level routing does not inherit MoE-style balancing in a straightforward way, and
> **long-context evaluation exposes failures that are nearly invisible in broad short-context
> benchmarks**."*
>
> **An upcycled model can look fine on standard benchmarks and break at long context.** If you
> upcycle, evaluate at your real context length, not at 4K.

### Frankenmerge / passthrough

Stacking layers from different checkpoints to build a deeper model. **Same-family only**, same
constraint as §1, and generally requires healing fine-tuning afterward.

---

## 3. Knowledge transfer — the actual cross-family answer

**This is what you want if the models are from different families.** It is not free: it is a training
run. But it is the only thing that genuinely crosses the boundary.

### The core obstacle: tokenizers

> *"Cross-tokenizer distillation... **remains a largely unsolved problem**. A fundamental limitation
> of conventional approaches is that they assume both models share the same vocabulary and tokenizer,
> a requirement that is **increasingly impractical**."*

Two models tokenize the same sentence into different token sequences. Distillation normally matches
output distributions **token by token** — with different tokenizers there is no shared axis to match on.

### The four strategies for beating it

**1. Map the tokens.**
**FuseLLM / Knowledge Fusion** aligns vocabularies using **MinED (minimum edit distance)** to map
tokens between tokenizers by string similarity. **Breaking the Tokenizer Barrier** brings **on-policy
distillation across model families** with a precise token-mapping algorithm.

**2. Drop to a common interface — bytes.**
**Byte-Level Distillation (BLD)** converts the teacher's output distribution to **byte-level
probabilities** and attaches a lightweight **byte-level decoder head** to the student. **Every
tokenizer agrees on bytes** — an elegant sidestep rather than a mapping heuristic.

**3. Optimal transport.**
**MultiLevelOT** treats alignment as a transport problem and is *"robust to different student and
teacher models across model families, architectures, and parameter sizes."* **CoT2Align** applies OT
to chain-of-thought distillation specifically. OT-based correspondence is described as an **active
area showing early promise as of February 2026** — i.e. promising, not settled.

**4. Map parameters, then distil.**
**Llamion** demonstrates cross-architecture transfer by **parameter-level mapping into a standardised
template, followed by cross-architecture distillation** — a two-stage hybrid of §1 and §3.

**Also:** **MoL (Mixture of Layers)** supports different tokenizers *and* architectures via
similarity-based functional distillation.

**What this unlocks**, per the literature: tokenizer transplantation, vocabulary expansion, teacher–
student transfer between families, and **ensembling, merging and speculative decoding across tokenizer
boundaries** — the last one connects directly to `dflash2 hwmini.md`, where drafter/target tokenizer
mismatch is the constraint.

---

## 4. Adapters — the practical answer for most people

**LoRA adapters are the pragmatic middle ground.** A LoRA *is* a task vector, so all of §1's arithmetic
applies — but on ~1% of the parameters, and **swappable at serve time without touching base weights**.

**Merging strategies in Hugging Face PEFT:** **Linear** · **Cat** (concatenation) · **TIES** ·
**Magnitude Prune** · plus weighted averaging and SVD compression — *"each presenting distinct
trade-offs in expressivity, memory efficiency, and compatibility."*

**Beyond fixed weights:**
- **LoRAHub** — **learns** adaptive fusion weights few-shot, instead of hand-tuned coefficients
- **Task-Aware LoRA Composition** — retrieves the right adapters from a **vector database** per task
- **LoRA Adapter Routing using Task Representations** — routing rather than merging
- **Retrieval-Augmented Mixture of LoRA Experts** — MoE, but over adapters

> ### The production failure mode, stated plainly
> *"Teams build separate LoRA adapters for tone, format, domain knowledge, and safety — **then hit
> conflicts when composing them**."*
>
> **Adapters compose until they don't.** Safety and tone adapters in particular fight, because both
> touch output style. Detecting interference and choosing the right merge strategy is what lets you
> **serve mixed adapters per request without reloading weights.**

**⚠️ Adapters are still same-base-model.** A LoRA trained on Llama does not load onto Qwen. Adapters
solve *composition*, not *cross-family*.

---

## 5. Decision guide

```
Do the models share a base checkpoint?
├─ YES ─► Weight merging (§1). Free, no training.
│         2 models .......... SLERP
│         3+ models ......... TIES  (+ DARE preprocessing)
│         add/remove a skill  Task Arithmetic
│         only adapters ..... PEFT merge, or LoRAHub to learn the weights
│
└─ NO (different families) ─► Weight merging will NOT work.
          │
          ├─ Want B to gain A's skill ──► Knowledge transfer (§3)
          │     same tokenizer? ......... standard distillation
          │     different tokenizer? .... BLD (bytes) · MultiLevelOT · on-policy
          │                               w/ token mapping · Llamion
          │
          ├─ Want both models' outputs ─► Don't merge. ENSEMBLE or ROUTE at
          │                               inference. Cheaper and it works today.
          │
          └─ Want lower memory ────────► Sparse upcycling (§2) on ONE model.
                                         Not a merge. Test at long context.
```

**The most under-used answer is "don't merge — route."** Two models behind a router give you both
capabilities today, with zero training, at the cost of holding both. On a 24 GB machine that is often
infeasible — which is precisely why merging is attractive, and precisely why it is oversold.

---

## 6. Honest gaps

- **No paper here was read in full.** All findings come from search results, abstracts and survey
  coverage. Every arXiv ID is cited so it can be checked.
- **Nothing was run.** No merge was performed, no result reproduced.
- **The "cross-family merging doesn't work" claim is a synthesis** of the field's own framing, not a
  single citable proof. It is well-supported and consistently stated, but it is a summary judgement.
- **OT-based cross-architecture merging is moving.** *"Early promise as of February 2026"* — the one
  area where this file could go stale fastest.
- **Frankenmerge/passthrough was covered thinnest** — one paragraph, no sources read.
- **No cost figures.** How much compute cross-tokenizer distillation actually needs was not
  established, and it is the deciding practical question.
- **DARE's 99% figure** is quoted from secondary coverage of the DARE paper, not the paper itself.

## 7. Sources

1. [Arcee's MergeKit: A Toolkit for Merging Large Language Models — arXiv 2403.13257](https://arxiv.org/pdf/2403.13257)
2. [A Systematic Study of In-the-Wild Model Merging for LLMs — arXiv 2511.21437](https://arxiv.org/pdf/2511.21437)
3. [Knowledge Fusion of Large Language Models (FuseLLM) — arXiv 2401.10491](https://arxiv.org/pdf/2401.10491) — MinED token alignment
4. [Activation-Informed Merging of LLMs — arXiv 2502.02421](https://arxiv.org/pdf/2502.02421)
5. [CAMEx: Curvature-aware Merging of Experts — arXiv 2502.18821](https://arxiv.org/pdf/2502.18821)
6. [`yule-BUAA/MergeLM`](https://github.com/yule-BUAA/MergeLM) — ICML 2024 codebase
7. [An Introduction to Model Merging for LLMs — NVIDIA](https://developer.nvidia.com/blog/an-introduction-to-model-merging-for-llms/)
8. [Merge, Ensemble, and Cooperate! A Survey — arXiv 2407.06089](https://arxiv.org/pdf/2407.06089)
9. [Drop-Upcycling: Training Sparse MoE with Partial Re-initialization — arXiv 2502.19261](https://arxiv.org/pdf/2502.19261)
10. [Upcycling Instruction Tuning from Dense to MoE via Parameter Merging — arXiv 2410.01610](https://arxiv.org/pdf/2410.01610)
11. [SPRI: SVD-Partitioned Residual Initialization for Data-Constrained MoE Upcycling — arXiv 2606.16456](https://arxiv.org/pdf/2606.16456)
12. [EMO: Frustratingly Easy Progressive Training of Extendable MoE — arXiv 2605.13247](https://arxiv.org/pdf/2605.13247)
13. [Continual LLM Upcycling — arXiv 2606.10722](https://arxiv.org/html/2606.10722)
14. [Breaking the Tokenizer Barrier: On-Policy Distillation across Model Families — arXiv 2606.09456](https://arxiv.org/pdf/2606.09456)
15. [Cross-Tokenizer LLM Distillation through a Byte-Level Interface — OpenReview](https://openreview.net/forum?id=WtmiQJr0jM)
16. [Multi-Level Optimal Transport for Universal Cross-Tokenizer KD — arXiv 2412.14528](https://arxiv.org/html/2412.14528)
17. [CoT2Align: Cross-CoT Distillation via Optimal Transport — arXiv 2502.16806](https://arxiv.org/pdf/2502.16806)
18. [Universal Cross-Tokenizer Distillation via Approximate Likelihood Matching — arXiv 2503.20083](https://arxiv.org/pdf/2503.20083)
19. [Llamion Technical Report — arXiv 2605.25676](https://arxiv.org/pdf/2605.25676)
20. [🤗 PEFT welcomes new merging methods](https://huggingface.co/blog/peft_merging) — Linear, Cat, TIES, Magnitude Prune
21. [Task-Aware LoRA Adapter Composition via Similarity Retrieval — arXiv 2602.21222](https://arxiv.org/pdf/2602.21222)
22. [Effective LoRA Adapter Routing using Task Representations — arXiv 2601.21795](https://arxiv.org/pdf/2601.21795)
23. [Retrieval-Augmented Mixture of LoRA Experts — arXiv 2406.16989](https://arxiv.org/pdf/2406.16989)
24. [LoRA Adapter Composition in Production — TianPan.co](https://tianpan.co/blog/2026-04-19-lora-adapter-composition-production)

**Related in this vault:** `UHWmini.md` §6b (sparse upcycling as a memory lever) · `dflash2 hwmini.md`
(tokenizer match as a speculative-decoding constraint) · `LLM train/Unsloth-finetune&train.md` and
`LLM train/Soup-finetune&train.md` (the training runs any §3 method requires) · `OrbiOSS.md` (the
model families you would be merging).

## Change Log

- **2026-09-02** — Created in sample 3. Researched inline rather than through the `/deep-research`
  workflow, which had failed twice earlier in this session at its adversarial-verification stage.
  **Principal finding, which structures the whole file: cross-family *weight merging* does not work,
  and the literature states so directly** — *"current LLM merging methods are typically restricted to
  models with same architecture and compatible parameters... most open-source LLMs are heterogeneous,
  rendering current merging methods ineffective."* Established that three distinct things get called
  "merging" and only one crosses families: **weight merging** (same base only), **architectural
  surgery** (one model at a time), and **knowledge transfer** (the real answer, and not merging).
  Documented weight merging over **task vectors** — Linear/Soup, Task Arithmetic, SLERP, **TIES**
  (sign-conflict resolution) and **DARE**, which drops **up to 99%** of task-vector weights before
  rescaling, implying task vectors are extremely redundant — plus mergekit, MergeLM,
  Activation-Informed Merging and CAMEx.
  Covered **sparse upcycling** precisely (copy each block's MLP E times, add a learnable top-k router,
  with router init coordinated to **maintain functional parity with the dense model at startup**),
  its 2026 refinements (Drop-Upcycling's partial re-initialisation, SPRI, EMO, Continual Upcycling),
  and the warning that it is **not lossless** — *"long-context evaluation exposes failures that are
  nearly invisible in broad short-context benchmarks"* — so upcycled models must be tested at real
  context length.
  Recorded the four cross-family knowledge-transfer strategies: **token mapping** (FuseLLM's MinED,
  on-policy distillation across families), **byte-level interface** (BLD converting teacher output to
  byte probabilities — every tokenizer agrees on bytes), **optimal transport** (MultiLevelOT,
  CoT2Align), and **parameter mapping then distillation** (Llamion) — noting the field's own
  assessment that cross-tokenizer distillation *"remains a largely unsolved problem."*
  Covered adapters as the pragmatic middle ground (PEFT's Linear/Cat/TIES/Magnitude-Prune, LoRAHub's
  learned fusion weights, vector-DB adapter retrieval, MoE-over-LoRA) with the production caveat that
  **adapters compose until they don't** — tone and safety adapters conflict because both shape output
  — and the reminder that adapters are still same-base-model.
  Added a decision guide whose most under-used branch is stated plainly: **when models are from
  different families and you want both capabilities, do not merge — route or ensemble at inference.**
  Zero training, works today, at the cost of holding both models — which is exactly why merging is
  attractive on a 24 GB machine and exactly why it is oversold.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** block at the top, matching sample 1's
  presentation style: what the file is, the numbers that matter, and the decisive caveat, all before
  any discussion. No content changed; the research below now serves as backing detail.
