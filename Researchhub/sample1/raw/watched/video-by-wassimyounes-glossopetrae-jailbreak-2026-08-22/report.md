---
source: https://www.instagram.com/reel/DZ0wq0GJ1Yr/
title: Video by wassimyounes_
duration: 00:48
watched_at: 2026-08-22T07:36:39.240782+07:00
intent: research about it, deep-research topic
hero_frames: [frame_0001.jpg, frame_0009.jpg, frame_0017.jpg, frame_0025.jpg, frame_0033.jpg]
transcript_source: none
---

# Video by wassimyounes_

## TL;DR

- Reel promotes elder-plinius's GLOSSOPETRAE project and its "Lingua Ex Machina" paper as a "universal jailbreaking prompt."
- Real finding is narrower and more interesting: a tokenizer-disagreement covert channel lets two AI models pass a hidden message past a third monitoring model (100% delivery, 0% detection, p<10^-7).
- The paper also ships its own fix (a two-line Unicode sanitization filter) alongside the attack.
- Sits inside a broader, independently peer-reviewed research area (multilingual/low-resource-language jailbreaking) that the reel doesn't mention.
- Full write-up: `Research docs/LLM-autotrain.md` in this vault.

## Key moments

- **[00:00] Hook** — narrator claims a known AI jailbreaker just released a "universal jailbreaking prompt" 20 minutes prior.
- **[00:08-00:20] Mechanism claim** — AI made to talk to itself in a non-human language to bypass its own guardrails; framed as "the gospel of all AI jailbreak."
- **[00:10, frame_0009.jpg]** — GitHub repo shown: `elder-plinius/GLOSSOPETRAE`, "BREAKING NEWS — UNIVERSAL JAILBREAKING PROMPT."
- **[00:11, frame_0010.jpg]** — README: "GLOSSOPETRAE — Procedural Xenolinguistics — Language Generation, Acquisition, Covert Channels," AGPL-3.0.
- **[00:25, frame_0020.jpg]** — Results table: "500/500 functional languages with phonology, morphology, syntax, lexicon..."
- **[00:29-00:38, frames 0025/0033]** — X/Twitter post from @elder_plinius announcing the "Lingua Ex Machina" paper: zero-shot language acquisition, human-unreadable code, exploitable covert channels.
- **[00:44] CTA** — "Comment 'jailbreak' and I'll send it over."

## Hook microscope (0-10s)

- Frames: 20 at 2 fps

Contrarian/shock-claim hook: opens on a flat, high-confidence assertion ("just made a universal jailbreaking prompt to crack every LLM out there") layered over a screen-recorded GitHub repo already showing a red "BREAKING NEWS" banner — the visual (a real, dated repo) lends credibility to the claim before any explanation. Classic demo-first/proof-first pattern: show the artifact, then narrate the (compressed, oversold) explanation.

## Editorial profile

_No scene-change data — likely a static/screen-recorded source._

Talking-head-over-screen-recording explainer, dense on-screen caption overlays synced to speech, no B-roll — typical fast-turnaround AI-news-commentary format built for muted autoplay.

## Quotable moments

- "[00:00] The person that keeps jailbreaking every LLM out there just made a universal jailbreaking prompt to crack every LLM out there."
- "[00:15] To bypass its own safety guardrails, so it plays offensively on its own self."
- "[00:25] This is like the gospel of all AI jailbreak."
- "[00:38] It creates a whole language by itself, human unreadable coding system, and exploits its own self."

## Entities mentioned

- People: [[elder-plinius]] (Pliny the Liberator), [[wassimyounes_]] (reel creator)
- Companies: [[anthropic]], [[openai]] (referenced as monitored model families in the paper)
- Tools / products: [[glossopetrae]], [[claude]], [[gpt]]
- Places: (none)

## Concepts surfaced

- **Procedural xenolinguistics**: generating a complete, internally consistent constructed language from a single numeric seed.
- **Zero-shot language acquisition**: a frontier model reading/writing/coding in a language it has never seen in training, purely from an in-context specification.
- **Tokenizer covert channel**: exploiting disagreement between model families' tokenizers over which Unicode characters survive preprocessing, to pass a hidden message past a monitoring model whose tokenizer strips the carrier.
- **Multilingual jailbreak**: broader, independently peer-reviewed finding that safety training is weaker in low-resource/unusual languages than in English.

## Transcript

Local whisper.cpp transcript (Instagram supplied no captions):

"The person that keeps the jailbreaking every LLM out there just made a universal jailbreaking prompt to crack every LLM out there. And it just went live 20 minutes ago. He found out that AIs could talk to themselves with a different language barrier than just English or any type of language out there. To bypass its own safety guardrails, so it plays offensively on its own self. So they use their own language to bypass their own safety. Token frontier to all these functional languages within itself. This is like the gospel of all AI jailbreak. And he made a whole internal research on this once again. It creates a whole language by itself human unreadable coding system and exploits its own self. Where it jail breaks all of its barriers guardrails and the research paper is out if you guys do want the repo though. Comment down below jailbreak and I'll send it over."

## All frames

_Total: 40. Hero frames flagged with star._

* `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0001.jpg` (t=00:00)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0002.jpg` (t=00:01)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0003.jpg` (t=00:02)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0004.jpg` (t=00:04)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0005.jpg` (t=00:05)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0006.jpg` (t=00:06)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0007.jpg` (t=00:07)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0008.jpg` (t=00:08)
* `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0009.jpg` (t=00:10)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0010.jpg` (t=00:11)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0011.jpg` (t=00:12)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0012.jpg` (t=00:13)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0013.jpg` (t=00:14)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0014.jpg` (t=00:16)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0015.jpg` (t=00:17)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0016.jpg` (t=00:18)
* `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0017.jpg` (t=00:19)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0018.jpg` (t=00:20)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0019.jpg` (t=00:21)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0020.jpg` (t=00:23)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0021.jpg` (t=00:24)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0022.jpg` (t=00:25)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0023.jpg` (t=00:26)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0024.jpg` (t=00:27)
* `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0025.jpg` (t=00:29)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0026.jpg` (t=00:30)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0027.jpg` (t=00:31)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0028.jpg` (t=00:32)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0029.jpg` (t=00:33)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0030.jpg` (t=00:35)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0031.jpg` (t=00:36)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0032.jpg` (t=00:37)
* `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0033.jpg` (t=00:38)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0034.jpg` (t=00:39)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0035.jpg` (t=00:41)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0036.jpg` (t=00:42)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0037.jpg` (t=00:43)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0038.jpg` (t=00:44)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0039.jpg` (t=00:45)
  `/Users/minhduc/.claude/jobs/173df9d5/tmp/watch6/frames/frame_0040.jpg` (t=00:47)
