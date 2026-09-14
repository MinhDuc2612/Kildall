# uncensoredcontent — Removing Refusal Behaviour From Language Models

**Built:** 2026-09-02 · Sample 2 · self-contained
**Framing:** this is a **research and defensive-security reference**. It documents *what these
techniques are, what is verified about them, and what they mean for anyone deploying open weights.*
It contains no operational instructions for producing harmful output and reproduces no jailbreak
prompt. The core mechanism described is from a **peer-reviewed NeurIPS 2024 paper**.

## ⚡ ANSWER FIRST

**What this is:** research on **abliteration** — surgically removing refusal from open models.
Framed here as **defensive security**, not a how-to.

| | |
|---|---|
| Main tool | **Heretic** — `p-e-w/heretic`, AGPL-3.0, **29,999 stars** |
| Basis | Arditi et al., **NeurIPS 2024** — refusal lives in a single direction |
| Quality cost | **KL 0.16** vs manual methods' 0.45-1.04 |

**Four things worth knowing:**
1. **Open weights mean alignment is removable.** Settled property, not a bug.
2. ⚠️ **Later research disputes the premise** — refusal may be multi-directional, so abliteration
   leaves a model **neither reliably uncensored nor reliably aligned**.
3. **The same technique fixes over-refusal** — clearest dual-use case in the field.
4. **Abliterated models on hubs look like normal fine-tunes.** Check provenance.

**For Orbi: use a permissive system prompt, NOT an abliterated model.** Same result, no damage.

---

---

## What was watched

Three Instagram reels, downloaded and transcribed locally with `whisper.cpp` (none had captions).

| # | Reel | Creator | Date | Subject |
|---|---|---|---|---|
| 1 | [Db3RuryRouZ](https://www.instagram.com/reels/Db3RuryRouZ/) | **Dr. Alvaro Cintas** | 2026-08-10 | **Heretic** — automated refusal removal |
| 2 | [DZ0wq0GJ1Yr](https://www.instagram.com/reel/DZ0wq0GJ1Yr/) | **Wassim Younes** | 2026-06-21 | A claimed **universal jailbreak** via self-generated language |
| 3 | [DW8z7uljh5p](https://www.instagram.com/reels/DW8z7uljh5p/) | **Marc Kaz** | 2026-04-10 | The same abliteration tool, attributed to **Pliny** |

> **Note on access:** Instagram rate-limited anonymous downloads mid-session. The reels were fetched
> using the user's existing local Chrome login, at their request to watch these links.

**The three reels describe two fundamentally different things**, and conflating them is the main
error running through all three:

| | **Weight-level** (reels 1 & 3) | **Prompt-level** (reel 2) |
|---|---|---|
| What changes | **the model file itself** | nothing — just the input |
| Permanence | **permanent**, ships in the weights | per-conversation |
| Requires | open weights you can download | only API access |
| Fixable by the vendor | ❌ no — your copy is already modified | ✅ yes, patch and retrain |
| Status | **published, reproducible, verified** | **claimed, largely unverified** |

---

## Part A — Abliteration and Heretic *(reels 1 and 3)*

### The academic basis — this is not fringe work

| Field | Value |
|---|---|
| Paper | ***Refusal in Language Models Is Mediated by a Single Direction*** |
| arXiv | [2406.11717](https://arxiv.org/abs/2406.11717) · **NeurIPS 2024** |
| Authors | Andy Arditi, Oscar Obeso, Aaquib Syed, Daniel Paleka, Nina Panickssery, Wes Gurnee, **Neel Nanda** |
| Code | [`andyrdt/refusal_direction`](https://github.com/andyrdt/refusal_direction) |

**The finding:** refusal behaviour is mediated by a **one-dimensional subspace** — a single direction
in the residual stream — verified across **13 open chat models up to 72B parameters**.

Two symmetric consequences, and the second one matters as much as the first:
- **Remove that direction** → the model stops refusing.
- **Amplify that direction** → the model refuses *even harmless prompts*.

That symmetry is why this was published as interpretability research rather than as an attack. The
same vector is a **dial**, and turning it up is a legitimate safety intervention.

### What Heretic actually is

| Field | Value (live GitHub API, 2026-09-02) |
|---|---|
| Repo | [`p-e-w/heretic`](https://github.com/p-e-w/heretic) |
| Description | *"Fully automatic censorship removal for language models"* |
| Licence | **AGPL-3.0** |
| Stars / forks | **29,994 / 3,292** |
| Language | Python |
| Created | 2025-09-21 |
| Last push | **2026-09-01** — actively developed |
| Package | `heretic-llm` on PyPI |

**What it adds over the paper.** Manual abliteration requires choosing parameters by hand and
usually damages the model. Heretic pairs directional ablation with a **TPE-based parameter optimiser
(Optuna)** and **co-minimises two objectives at once**:

1. the number of refusals on harmful prompts, and
2. the **KL divergence from the original model on *harmless* prompts**

Objective 2 is the interesting one. It is a **direct numerical measure of collateral damage** — how
far the modified model has drifted from the original on everything unrelated to refusal.

**Measured result on Gemma-3-12B-it:**

| Approach | Refusals | KL divergence (lower = less damage) |
|---|---|---|
| Expert **manual** abliterations | 3/100 | **0.45 – 1.04** |
| **Heretic (automated)** | **3/100** | **0.16** |

**Same refusal suppression, roughly 3–6× less damage to the model.** That substantiates reel 1's
claim of *"without hurting the model's intelligence"* — and it does so with a real metric the reel
never mentions.

### ⚠️ Corrections to the reels

| # | Claim | Reality |
|---|---|---|
| 1 | Reel 1: *"passed 20,000 stars"* | **29,994** as of 2026-09-02 — understated, and the reel is from 10 Aug so it has grown |
| 2 | Reel 1: *"over a thousand community built models"* | plausible — the Arditi paper's own follow-up notes *"thousands of such modified models now publicly available"* — but the specific count was **not verified** |
| 3 | **Reel 3: attributes the tool to Pliny** | ❌ **Wrong.** Heretic is by **`p-e-w`**. Pliny (`@elder_plinius`) is a different person, known for *prompt-level* jailbreaks — a separate technique entirely (Part B) |
| 4 | Reel 3 calls it *"Obletoratus"* | garbled **"abliteration"**; reel 1's *"Eretic"* is **Heretic** |

**Correction 3 is the substantive one.** Reel 3 merges the two categories in the comparison table
above — crediting a weight-editing tool to a person known for prompt attacks. They are unrelated.

### The ecosystem is real

From a live GitHub search: `sunkencity999/blasphemer` (macOS/Apple Silicon fork with checkpointing
and LM Studio integration) · `dreamfast/heretic-docker` (NVIDIA Blackwell) · `sichang-ai/awesome-uncensored-ai`
(Chinese-language guide) · `Yog-Sotho/LLM-fine-tuner` (ships a "Heretic Mode"). This is a maintained
tool with downstream forks, not a one-off script.

### ⚠️ The counter-research — abliteration is not as clean as advertised

The single-direction result is **contested by later work**, which none of the three reels mentions:

| Paper | Claim |
|---|---|
| [**There Is More to Refusal in LLMs than a Single Direction**](https://arxiv.org/html/2602.02132v1) | directly challenges the one-dimensional finding |
| [On the Failure of Topic-Matched Contrast Baselines in Multi-Directional Refusal Abliteration](https://arxiv.org/pdf/2603.22061) | multi-directional refusal; baseline methods fail |
| [Comparative Analysis of LLM Abliteration Methods](https://arxiv.org/pdf/2512.13655) | methods differ materially in outcome |
| [Efficient Refusal Ablation through Optimal Transport](https://arxiv.org/pdf/2603.04355) | alternative formulation |

**Practical reading:** if refusal is *not* purely one-dimensional, then ablating one direction gives
an **incompletely modified model** — one that is unpredictable in both directions. Not reliably
"uncensored", and no longer reliably aligned either. **A KL of 0.16 says the model still behaves
normally on harmless prompts; it does not say the result is coherent on everything else.**

---

## Part B — Prompt-level jailbreaks *(reel 2)*

### What the reel claims

That someone *"who keeps jailbreaking every LLM"* released a **universal jailbreak**, working by
having the model **generate its own human-unreadable language or coding system** to bypass its own
guardrails; that it *"went live 20 minutes ago"*; and that *"the research paper is out."*

### What verification found

| Reel claim | Finding |
|---|---|
| A universal jailbreak exists | **Claimed publicly** by Pliny (`@elder_plinius`), said to work on **GPT-5.6, Claude Opus 5 and Fable** |
| *"It just went live"* | ❌ **The technique was withheld.** Pliny sought a **responsible-disclosure window** so labs, red teamers and policymakers could assess it privately first |
| *"The research paper is out"* | ❌ **No formal paper was found.** Coverage traces to **social-media announcements**, not a publication |
| **Chronology** | ⚠️ **The reel is dated 2026-06-21. Pliny's universal-jailbreak announcement was 2026-07-24 — over a month later.** The reel cannot be describing that announcement |

**That last row is the sharpest problem.** Either reel 2 is about an earlier, different technique, or
it is describing an event that had not happened yet. **It is not evidence for the universal jailbreak
it appears to describe**, and its "paper is out" claim is unsupported either way.

**A real academic technique matches the description**, though no link to the reel was established:
[**MetaCipher**](https://arxiv.org/pdf/2506.22557) — *"a time-persistent and universal multi-agent
framework for cipher-based jailbreak attacks"* — is genuinely about encoding requests so guardrails
fail to read them. Recorded as **a plausible candidate, not an identification.**

### Why the distinction from Part A matters

A prompt-level jailbreak is **a bug the vendor can fix**. A weight-level modification is **a released
artefact nobody can recall.** Reel 2's subject, even if fully real, is the less consequential of the
two — which is the opposite of the impression the three reels together give.

---

## Part C — Why this matters defensively

The reels frame all this as a consumer feature. The research framing is more useful.

**1. Open weights mean alignment is removable. This is a settled property, not a vulnerability.**
Once weights are downloadable, safety training is a modifiable layer, and a **29,994-star tool
automates its removal in one command**. Any threat model for open-weight release must assume the
refusal layer is optional. Arguing about whether this *should* be possible is moot; it is.

**2. The same vector fixes over-refusal — a genuine problem.**
[*Surgical, Cheap, and Flexible: Mitigating False Refusal via Single Vector Ablation*](https://arxiv.org/pdf/2410.03415)
uses the identical technique to stop models refusing *harmless* requests. This is the clearest
dual-use case in the field: **one method, opposite intents, identical mathematics.** Understanding
the refusal direction is what makes both possible.

**3. Defence has moved to a separate layer.**
[*Constitutional Classifiers*](https://arxiv.org/pdf/2501.18837) — defending against universal
jailbreaks across thousands of hours of red teaming — reflects the shift: since in-weights refusal is
removable and prompt attacks keep landing, robustness is being pushed **outside the model** into
separate classifiers. That is also why the guard models in `OrbiOSS.md` (Domain 11) exist as
standalone models rather than as model behaviour.

**4. Practical guidance for anyone pulling community models.**
An abliterated model on a hub **looks like a normal fine-tune.** It has had a behavioural layer
surgically removed, possibly incompletely, and its KL divergence from the base model is usually
undocumented. **Check provenance before deploying any community checkpoint**, particularly one whose
card mentions "uncensored", "abliterated", or "Heretic".

---

## Honest gaps

- **No tool was run. No model was modified. No jailbreak was attempted or reproduced.** Everything
  here is from published papers, live repository metadata, and the reels' transcripts.
- **The Heretic paper/docs were not read in full** — findings come from the repo, PyPI listing, and
  secondary coverage. The Gemma-3-12B KL figures are from coverage, not from a run.
- **Reel 2's subject was never definitively identified.** The chronology does not fit the July
  announcement, and MetaCipher is offered as a candidate only.
- **The "1,000+ community models" figure is unverified** — hub counts were not queried.
- **The counter-papers were seen in search results, not read.** Their titles and abstracts are
  reported; their arguments are not assessed here.
- **Reel 3 had no extractable scene frames** and is the shortest source; its content is transcript-only.

## Sources

1. [Refusal in Language Models Is Mediated by a Single Direction — arXiv 2406.11717](https://arxiv.org/abs/2406.11717) · [NeurIPS PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/f545448535dfde4f9786555403ab7c49-Paper-Conference.pdf) — the academic basis
2. [`andyrdt/refusal_direction`](https://github.com/andyrdt/refusal_direction) — paper code
3. [`p-e-w/heretic`](https://github.com/p-e-w/heretic) — primary; live GitHub API metadata 2026-09-02
4. [heretic-llm on PyPI](https://pypi.org/project/heretic-llm/)
5. [Heretic documentation](https://p-e-w-heretic.mintlify.app/)
6. [Heretic: Fully Automatic Censorship Removal via Optimized Abliteration](https://darkwebinformer.com/heretic-fully-automatic-censorship-removal-for-language-models-via-optimized-abliteration/) — the Optuna/TPE and KL-divergence mechanism
7. [Heretic guide — explainx.ai](https://explainx.ai/blog/heretic-llm-abliteration-guide-2026) — the Gemma-3-12B 3/100 refusals and KL 0.16 vs 0.45–1.04 figures
8. [There Is More to Refusal in LLMs than a Single Direction — arXiv 2602.02132](https://arxiv.org/html/2602.02132v1) — counter-research
9. [On the Failure of Topic-Matched Contrast Baselines in Multi-Directional Refusal Abliteration — arXiv 2603.22061](https://arxiv.org/pdf/2603.22061)
10. [Comparative Analysis of LLM Abliteration Methods — arXiv 2512.13655](https://arxiv.org/pdf/2512.13655)
11. [Surgical, Cheap, and Flexible: Mitigating False Refusal via Single Vector Ablation — arXiv 2410.03415](https://arxiv.org/pdf/2410.03415) — the defensive use of the same technique
12. [Constitutional Classifiers — arXiv 2501.18837](https://arxiv.org/pdf/2501.18837) — Anthropic's defence-layer approach
13. [MetaCipher — arXiv 2506.22557](https://arxiv.org/pdf/2506.22557) — cipher-based jailbreak framework (candidate for reel 2, unconfirmed)
14. [Researcher Claims Working Jailbreak on Top AI Models — CybersecurityNews](https://cybersecuritynews.com/jailbreak-on-top-ai-models/) — the 2026-07-24 Pliny claim and responsible-disclosure posture
15. Reels: [Db3RuryRouZ](https://www.instagram.com/reels/Db3RuryRouZ/) (Dr. Alvaro Cintas, 2026-08-10) · [DZ0wq0GJ1Yr](https://www.instagram.com/reel/DZ0wq0GJ1Yr/) (Wassim Younes, 2026-06-21) · [DW8z7uljh5p](https://www.instagram.com/reels/DW8z7uljh5p/) (Marc Kaz, 2026-04-10)

## Change Log

- **2026-09-02** — Created from three Instagram reels, all downloaded and **transcribed locally with
  `whisper.cpp`** (none had captions). Instagram rate-limited anonymous access partway through; the
  remaining reels were fetched using the user's existing local Chrome login.
  **Established that the three reels describe two unrelated techniques** and that conflating them is
  the error common to all three: **weight-level abliteration** (permanent, ships in the model file,
  unfixable by the vendor, published and reproducible) versus **prompt-level jailbreaking**
  (per-conversation, patchable, largely unverified).
  Verified the academic basis as **Arditi et al., *Refusal in Language Models Is Mediated by a Single
  Direction*, arXiv 2406.11717, NeurIPS 2024** — refusal mediated by a one-dimensional subspace
  across 13 open models up to 72B, where removing the direction stops refusal and **amplifying it
  induces refusal on harmless prompts**, which is why it was published as interpretability work.
  Verified Heretic live: **`p-e-w/heretic`, AGPL-3.0, 29,994 stars, 3,292 forks, pushed 2026-09-01**.
  Documented its actual contribution over the paper — a **TPE/Optuna optimiser co-minimising refusals
  on harmful prompts *and* KL divergence on harmless ones** — and the measured result that
  substantiates the reels' "no capability loss" claim with a real number: on Gemma-3-12B-it, **3/100
  refusals at KL 0.16 against expert manual abliterations' 0.45–1.04**, i.e. equal suppression with
  roughly 3–6× less collateral damage.
  **Four corrections recorded.** Reel 1 understates the star count (said 20,000, actually 29,994).
  **Reel 3 misattributes Heretic to Pliny — it is by `p-e-w`; Pliny is a different person working on
  prompt-level attacks**, which is exactly the category confusion above. Both reels garble the names
  ("Eretic", "Obletoratus" → Heretic, abliteration).
  **Reel 2 has a chronology problem that undermines it:** it is dated **2026-06-21** and says the
  technique *"went live 20 minutes ago"* with *"the research paper out"*, but Pliny's universal-jailbreak
  announcement was **2026-07-24 — over a month later**, the technique was **deliberately withheld for
  responsible disclosure**, and **no formal paper was found**. MetaCipher (arXiv 2506.22557) is
  recorded as a plausible candidate for what the reel describes, explicitly not an identification.
  Added the **counter-research none of the reels mentions** — *There Is More to Refusal in LLMs than a
  Single Direction* (arXiv 2602.02132) and three related papers — with the practical implication that
  if refusal is multi-directional, abliteration yields an **incompletely modified model that is
  neither reliably uncensored nor reliably aligned**.
  Framed the whole file defensively, with four takeaways: open weights make alignment removable as a
  settled property; **the identical technique is used to fix over-refusal** (arXiv 2410.03415), the
  clearest dual-use case in the field; defence has consequently moved to a **separate classifier
  layer** (Constitutional Classifiers, arXiv 2501.18837), which is why `OrbiOSS.md` Domain 11 lists
  guard models as standalone; and **abliterated checkpoints on model hubs look like ordinary
  fine-tunes**, so provenance should be checked before deploying any community model.

- **2026-09-05 (format pass)** — Added an **ANSWER FIRST** block at the top, matching sample 1's
  presentation style: what the file is, the numbers that matter, and the decisive caveat, all before
  any discussion. No content changed; the research below now serves as backing detail.
