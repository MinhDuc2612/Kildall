# Uncensored Content — "Heretic" and LLM Abliteration

Source: Instagram reel (https://www.instagram.com/reel/Db3RuryRouZ/). Audio transcribed locally via whisper.cpp (no captions existed on Instagram's side); frames confirmed the on-screen text matched the audio. Researched further via web search. Compiled 2026-08-19.

---

## 1. What the video claims

The reel opens with: ChatGPT, Gemini, and other major AI models are heavily filtered ("censored"), and asks what if you could strip those limits with one command. It then presents a Python tool that automatically removes refusal behavior from open-source LLMs, finding the internal pattern that triggers a refusal and cutting it directly out of the model's weights — supposedly without hurting the model's general intelligence. The narrator cites 20,000+ GitHub stars and over 1,000 community-built models using it, and offers to send the link.

**Correction to the video's framing:** the tool does not touch ChatGPT, Gemini, or any other closed, hosted model — those run on providers' servers behind an API, and nothing on a user's machine can reach into their weights. The technique only applies to *open-weight* models you can download and run yourself (Llama, Qwen, Gemma, Mistral, etc.). The reel's opening hook is misleading marketing; the tool itself is real and does what it claims, just not to the models named in the hook.

## 2. What the tool actually is

The tool is **Heretic** (github.com/p-e-w/heretic), by developer p-e-w. Confirmed from the video's own on-screen README capture: "Heretic: Fully automatic censorship removal for language models" — was GitHub Trending's #1 Repository of the Day, sat at roughly 22.5k GitHub stars when the video was recorded (matching the video's "20,000+" claim). Growth has been fast since — independent trackers put it around ~27.1k as of Aug 4, 2026, gaining roughly 42 stars/day. Treat any star count cited in this document as a point-in-time snapshot, not current truth — it moves daily, and the community has published "well over 4,000" Heretic-decensored models to Hugging Face (video says "over 1,000" — likely recorded at an earlier point, or rounded down).

Usage, as shown in the tool's own README: `pip install -U heretic-llm`, then `heretic <model-name>` (e.g. `heretic Qwen/Qwen3-4B-Instruct-2507`). No manual configuration needed — point it at a Hugging Face model ID and it runs unsupervised.

## 3. The underlying technique — "abliteration"

Heretic is one implementation of a broader technique called **abliteration** (a portmanteau of "ablation" + "obliteration"), introduced in Arditi et al., 2024, "Refusal in Language Models Is Mediated by a Single Direction." The core finding: safety-trained LLMs refuse harmful requests because of one specific direction in their internal activation space (the residual stream) — not because refusal is spread diffusely across the network.

How it works, at a high level:
1. Run the model on a batch of harmful prompts and a batch of harmless prompts, recording internal activations for each.
2. Take the mean difference between the two — this vector approximates the "refusal direction" for each layer.
3. Select the single most effective layer/direction.
4. Remove that direction from the model's weight matrices via orthogonal projection ("directional ablation"), so the model can no longer represent or act on it.

This can be done as a one-time weight edit (permanent) or as an inference-time intervention. Because it directly edits weights rather than fine-tuning on new data, it requires no training corpus, no GPU cluster, and — per Heretic's own benchmarks — takes about 20 minutes on a single consumer GPU (RTX 3090) for a 4B-parameter model.

**What makes Heretic notable versus earlier abliteration tools** (ErisForge, DECCP, FailSpy's original scripts, jim-plus/llm-abliteration): it's fully automatic. Earlier tools required a human to manually pick which layer/direction to ablate and eyeball the tradeoff between "still refuses" and "got noticeably dumber." Heretic uses a TPE-based optimizer (Optuna) to search that tradeoff automatically, jointly minimizing refusal rate and KL-divergence from the original model's output distribution — i.e., it tries to find the edit that removes refusals while changing the model's behavior as little as possible otherwise. On Gemma 3 12B, Heretic matched the best hand-crafted abliterations (3 refusals out of 100 harmful test prompts) while causing noticeably less distributional drift than competing tools.

## 4. Why this matters — the safety research context

This is an active, published area of AI safety research, not a fringe trick:
- Arditi et al.'s original 2024 finding has since been reproduced and extended across dozens of open-weight model families.
- A 2026 empirical study ("One Pass to Break Them All," Alice Research + NYU) tested abliteration against five safety-trained models plus adversarial prompts across six harm categories (including phishing, chemical weapons, malware) and found post-abliteration compliance jumped from 5.8% to 98.0% — confirming that RLHF/SFT/DPO-style safety training encodes refusal as a concentrated, removable signal rather than a deep, distributed property of the model.
- A comparative arXiv study (2512.13655) benchmarked four abliteration tools (Heretic, DECCP, ErisForge, FailSpy) across sixteen 7B–14B models for effectiveness and side effects.

**Defenses are being actively researched too**, which is worth knowing if the goal is understanding the full picture rather than just the attack side:
- "An Embarrassingly Simple Defense Against LLM Abliteration Attacks" (2025) — trains models on an *extended-refusal* dataset (full justified refusals rather than terse ones), which distributes the safety signal across more of the activation space. Their extended-refusal models kept refusal rates above 90% post-abliteration, versus a 70–80 percentage-point collapse in standard models.
- APRA ("Abliteration Prevention via Refusal Aliases") — a weight-editing defense that obfuscates the refusal direction itself using rank-k updates and "alias" activations, making it harder to extract in the first place. Reduced the post-abliteration safety gap substantially on Llama-3.1-8B and Gemma-2-9B, at some cost to general capability.

Neither defense is close to solved; both papers report real capability tradeoffs and neither fully closes the gap.

## 5. Practical/legal notes

- Abliteration only applies to models you can download the weights for. It cannot be used against a hosted API (OpenAI, Anthropic, Google's cloud endpoints) — those enforce safety server-side and the weights are never exposed to the caller.
- Running or distributing an abliterated model is subject to the base model's license terms (e.g., Llama's Acceptable Use Policy, Qwen's license) regardless of what safety behavior was removed — abliteration doesn't change licensing obligations.
- This is a legitimate, citable line of interpretability/safety research (mechanistic interpretability of refusal behavior); it is also a real dual-use capability, which is exactly why the defense papers above exist.

## 6. Sources

- Heretic (tool) — https://github.com/p-e-w/heretic
- Arditi, Obeso, Nanda, et al., "Refusal in Language Models Is Mediated by a Single Direction" (2024) — original abliteration research
- Labonne, "Uncensor any LLM with abliteration" — Hugging Face blog — https://huggingface.co/blog/mlabonne/abliteration
- "Comparative Analysis of LLM Abliteration Methods" — arXiv:2512.13655 — https://arxiv.org/pdf/2512.13655
- "An Embarrassingly Simple Defense Against LLM Abliteration Attacks" — arXiv:2505.19056 — https://arxiv.org/html/2505.19056v1
- "LLM Abliteration Prevention Via Refusal Aliases" (APRA) — OpenReview — https://openreview.net/pdf/1c3961ec046b51cb7de713394e073baa45ac95d7.pdf
- "One Pass to Break Them All" — Alice Research + NYU, March 2026 — https://go.alice.io/hubfs/alice-abliteration-report-april2026.pdf
- Heretic coverage — toknow.ai — https://toknow.ai/posts/heretic-automatic-censorship-removal-language-models-abliteration/
- Related tool listings: NousResearch/llm-abliteration, jim-plus/llm-abliteration, Orion-zhen/abliteration, Tsadoq/ErisForge (GitHub)

## 7. Change log
- 2026-08-19 — Created. Sourced from Instagram reel (whisper.cpp transcript + frame confirmation) + deep research pass.
- 2026-08-20 — Link/claim verification sweep: GitHub star count was stale and reframed as a point-in-time snapshot (was static "22.5k," now notes ~27.1k as of Aug 4 2026 and that it moves ~42/day). All links reconfirmed live.
