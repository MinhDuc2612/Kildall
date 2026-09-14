---
source: https://www.instagram.com/reel/DawbfDGPLOe/
title: Video by raycfu
duration: 01:13
watched_at: 2026-08-23T21:51:17.446275+07:00
intent: research about it, identify the tool/project/technique being discussed, deep-research topic
hero_frames: [frame_0001.jpg, frame_0005.jpg, frame_0009.jpg, frame_0013.jpg, frame_0020.jpg]
transcript_source: local-whisper-cpp
---

# Video by raycfu

## TL;DR

- Creator raycfu (Rui Fu) posts Part 2 of a series titled "How to build an Agentic OS using Fable 5" — a personal, hand-rolled autonomous-agent scaffold built on top of a Claude model the creator brands "Fable" (shown on-screen as "Claude Fable"), not a third-party open-source tool with its own GitHub repo shown in the reel.
- The system is a Markdown/bash-file repo skeleton (`CLAUDE.md`, `loop.sh`, `conductor.md`, `triage.md`, `contract.md`, `workers/`, `guardrails/`, `scripts/trust-log.sh`, `scripts/cost-check.sh`, `goals/`, `memory/STATE.md` etc.) that runs Claude in a repeating loop as an "AI employee."
- Three components close out the system (Part 1 covered the daily loop): (1) a self-enforced spending **budget** with per-step cost logging and a halt-if-over gate; (2) **model routing** — a cheap model (Haiku) handles routine checks, the expensive "Fable" model only wakes for real decisions (~60x cost/call); (3) four **optional upgrade loops** (sparring/builder-vs-breaker, compost/weekly rule-writing) plus a **Mission Control** dashboard triggered by a "Hey Jarvis" voice command.
- Explicitly framed as a 4-week trust ramp: Week 1 human watches everything, Week 2 it drafts, Week 3 it ships alone, Week 4 it proposes its own improvements.
- This is squarely an "agentic OS" build video (title literally uses that phrase) — but it documents one creator's personal DIY framework/workflow pattern rather than a distinct named open-source project; "Fable" itself needs external verification (see Concepts/entities below and last30days research file).

## Key moments

- **[00:00] Title card / hook** — "How to build an Agentic OS using Fable 5 — part 2" over creator sitting at a standing desk (`frame_0001.jpg`).
- **[00:04] Recap of part 1** — thumbnail of "part 1" shown with a "Claude Fable" logo card, references the daily loop system already built.
- **[00:07] Repo skeleton reveal** — code editor shows the full file tree: `CLAUDE.md` (the constitution), `loop.sh` (heartbeat), `conductor.md` (routing prompt), `triage.md`, `contract.md`, `workers/implement.md`, `workers/verify.md`, `guardrails/verify.md`, `scripts/trust-log.sh`, `scripts/log-cost.sh`, `scripts/cost-check.sh`, `quorum.sh`, `verify-goals.sh`, `goals/`, `skills/`, `memory/` (`STATE.md`, `trust.tsv`, `goal-ledger.tsv`, `dispatch.tsv`, `usage.log`) (`frame_0002.jpg`).
- **[00:09] Build #1: The Budget** — a "Ledger / Agent cost control" dashboard shows $4.771 of a $5.00 daily limit spent, with a "proceed if under, halt if over" gate and per-step cost logging (`frame_0005.jpg`, `frame_0006.jpg`).
- **[00:16-00:19] Model routing** — dashboard splits calls between "Haiku" (routine checks, 1,292 calls today, $0.001/call) and "Fable" (decisions only, ~40 calls today, $0.068/call, "~60x more per call — so it only wakes for real decisions") (`frame_0008.jpg`, `frame_0009.jpg`).
- **[00:24] Build #2: The Optional Loops** — bash script running `npm run typecheck`, `npm test`, `npm run lint` frames the 4 upgrade loops as opt-in, switched on only when a specific problem shows up (`frame_0010.jpg`).
- **[00:33-00:37] Sparring loop** — adversarial Builder vs. Breaker pattern: Breaker hunts for real weaknesses, Builder fixes them, neither touches the other's work (`frame_0012.jpg`, `frame_0013.jpg`).
- **[00:39-00:42] Compost loop** — runs weekly, reads every failure from the week (5-6 failures shown) and proposes up to 3 new rules, tightening strictness over time (`frame_0014.jpg`-`frame_0016.jpg`).
- **[00:46-00:47] Build #3: Mission Control** — a `/goal` markdown spec with permissions/walls/timebox rules, plus a dashboard triggered by voice command "Jarvis" showing pending approvals, an A- report card, and weekly spend ($186.40) (`frame_0017.jpg`, `frame_0018.jpg`).
- **[00:56-01:00] 4-week trust ramp payoff** — Week 1 "watched" → Week 2 "drafted" → Week 3 "shipped alone" (340 recipients, no review requested) → Week 4 "self-improved" (`frame_0019.jpg`, `frame_0020.jpg`).
- **[01:03-01:12] CTA** — "This is a full AI employee working for you nonstop... comment to get the step-by-step guide," standard engagement-bait close.

## Hook microscope (0-10s)

- Frames: 20 at 2 fps

Frame-by-frame: the reel opens cold on a bold yellow/white title card ("How to build an Agentic OS using Fable 5 — part 2") overlaid on the creator sitting at his desk — no spoken hook, the on-screen text IS the hook. By ~00:03-00:04 he cuts to himself talking, immediately referencing "part 1" with a thumbnail-in-thumbnail recap, then within 5-7s jumps straight to a code/dashboard screenshot (the repo file tree). This is a **sequel + demo-first hook**: it skips any "let me tell you a story" framing and assumes the viewer already wants the payoff (the file tree / system architecture) shown almost immediately. The pattern for the rest of the video repeats this beat: he says one sentence, then a UI/code screenshot fills ~2/3 of the frame to prove the claim, then he cuts back to camera for the next sentence. High information density for a sub-90s video.

## Editorial profile

- Shots: 20
- Cuts/min: 16.54
- Mean shot length: 3.63s
- Median shot length: 2.67s
- Talking-head ratio: n/a (opencv not installed)

Talking-head-to-screenshot ping-pong at ~16.5 cuts/min with short (2.7-3.6s) shots — classic "creator explains, screenshot proves it" tech-education format, heavy on-screen text captions burned in, no B-roll, single static camera/location (home desk setup).

## Quotable moments

- **[00:17]** "The expensive model never does the routine checking."
- **[00:21]** "Fable only wakes up when there is a real decision to make."
- **[00:43]** "Your agent system does not just do the work, it studies its own mistakes and gets stricter over time."
- **[00:59]** "Week one you watch everything, week two it drops, and week three it starts shipping on its own."
- **[01:03]** "This is a full AI employee working for you nonstop."

## Entities mentioned

- People: [[rui-fu]] (creator, @raycfu)
- Companies: [[anthropic]] (implied — Claude is Anthropic's model family; "Fable" branding not independently confirmed as an official Anthropic name)
- Tools / products: [[claude]], [[claude-haiku]], [[fable-5]] (creator's name/nickname for a Claude model tier — unverified as official), npm/lint/test tooling, a custom unnamed "Mission Control" dashboard, "Jarvis" (voice-command alias, not the historical Iron Man reference specifically — generic assistant nickname)
- Places: none

**Verification flag:** on-screen text repeatedly shows "Claude Fable" / "Fable 5" as if it is a specific, named Claude model or product. This could not be confirmed from the reel alone — cross-check against Anthropic's actual model lineup and community discussion before treating "Fable 5" as an official product name in any downstream doc.

## Concepts surfaced

- **Agentic OS**: the video's own framing — a persistent, self-running scaffold of files/scripts/prompts that lets an LLM operate as an "AI employee" over days/weeks rather than a single chat session.
- **Self-enforced budget gate**: the agent checks its own spend against a daily limit before each run and halts if over, with every step cost-logged.
- **Model routing / tiered cost control**: cheap model (Haiku) handles high-frequency routine checks; expensive model ("Fable") only invoked for real decisions — an economic argument for multi-model agent pipelines.
- **Sparring loop (builder/breaker adversarial pattern)**: two agent roles, one implements, one adversarially tests, neither edits the other's output — a lightweight self-play/red-team pattern for code quality.
- **Compost loop**: a weekly reflection job that mines the week's failures and proposes new rules, letting the system's guardrails tighten over time (a form of scaffolded self-improvement / meta-learning without weight changes).
- **Mission Control**: a human-facing dashboard/approval queue plus natural-language ("Hey Jarvis") status check-in, framed as the human oversight layer that gradually recedes.
- **4-week trust ramp**: a staged autonomy rollout (watch → draft → ship alone → self-improve) as a practical pattern for safely increasing agent autonomy.

## Transcript

_Source: local whisper.cpp (ggml-base.en.bin), not the API-key Whisper path — no captions were available from Instagram and no Groq/OpenAI key is configured in this environment._

[00:00.000 --> 00:03.040] Most people don't realize that Claude Fable 5 can become an AI employee and work for
[00:03.040 --> 00:04.560] hours on its own all automated.
[00:04.560 --> 00:06.960] In part 1, we got Claude Fable 5 running a daily loop system.
[00:06.960 --> 00:09.120] Here are the three builds that complete this agentic OS system.
[00:09.120 --> 00:09.600] The budget.
[00:09.600 --> 00:12.000] You give this system a spending limit that it enforces itself.
[00:12.000 --> 00:15.280] Each step gets logged with the cost and before each run, the system checks if the daily
[00:15.280 --> 00:15.920] limit has been hit.
[00:15.920 --> 00:17.440] But here's the rule that actually keeps it cheap.
[00:17.440 --> 00:19.360] The expensive model never does the routine checking.
[00:19.360 --> 00:22.400] Use a model like Haiku to do the checks and Fable only wakes up when there is a real
[00:22.400 --> 00:23.120] decision to make.
[00:23.120 --> 00:24.080] The optional loops.
[00:24.080 --> 00:27.680] This is a set of 4 upgrade loops and you only add them for a specific problem that shows up.
[00:27.680 --> 00:31.280] Sparring loop is when you run two AIs against each other, one builds, and one whose only
[00:31.280 --> 00:33.440] job is to find a weakness in yesterday's work and prove it.
[00:33.440 --> 00:35.360] The builder has to fix whatever the breaker finds.
[00:35.360 --> 00:36.880] And neither one can touch each other's work.
[00:36.880 --> 00:38.640] And then there's a compost loop that runs once a week.
[00:38.640 --> 00:41.840] And reads every failure from that week and proposes up to three new rules for the system.
[00:41.840 --> 00:44.960] So your agent system does not just do the work, it studies its own mistakes and gets
[00:44.960 --> 00:45.680] stricter over time.
[00:45.680 --> 00:46.480] Mission control.
[00:46.480 --> 00:49.920] You set the whole thing to run automatically every weekday at 7am and use one simple command
[00:49.920 --> 00:51.440] like "Hey Jarvis" to check on it.
[00:51.440 --> 00:54.480] One shows what is waiting for your approval, one shows your report card, and one shows
[00:54.480 --> 00:55.840] the budget that you still have left this week.
[00:55.840 --> 00:59.040] Week one you watch everything, week two it drafts, and week three it starts shipping
[00:59.040 --> 00:59.520] on its own.
[00:59.520 --> 01:01.760] And by week four it starts proposing its own improvements.
[01:01.760 --> 01:03.840] This is a full AI employee working for you nonstop.
[01:03.840 --> 01:07.440] I created a step by step guide on how to build out this exact Fable 5 agentic OS system.
[01:07.440 --> 01:10.000] If you want it, just like the video and comment "agent" and I'll send it to you.
[01:10.000 --> 01:12.400] Follow for more ways to make money and run your business with tech and AI.

_Note: whisper mis-transcribed a few words on first pass (e.g. "the role that actually" corrected to "the rule that actually" from re-listen of context; "one chose" corrected to "one shows" per sentence logic). Model name consistently rendered as "Claude Fable 5" / "Fable" — this matches on-screen text exactly, so it is very likely accurate, but "Fable" as an official Anthropic product/model name is NOT independently confirmed — see Entities section verification flag._

## All frames

_Total: 20. Hero frames flagged with star._

* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0001.jpg` (t=00:00)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0002.jpg` (t=00:05)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0003.jpg` (t=00:07)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0004.jpg` (t=00:08)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0005.jpg` (t=00:09)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0006.jpg` (t=00:12)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0007.jpg` (t=00:16)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0008.jpg` (t=00:17)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0009.jpg` (t=00:19)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0010.jpg` (t=00:23)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0011.jpg` (t=00:24)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0012.jpg` (t=00:33)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0013.jpg` (t=00:35)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0014.jpg` (t=00:37)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0015.jpg` (t=00:39)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0016.jpg` (t=00:42)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0017.jpg` (t=00:46)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0018.jpg` (t=00:47)
  `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0019.jpg` (t=00:56)
* `/var/folders/kd/h_54r2bn57n3r0xj5b8cy3s40000gn/T/watch-dvzmp_qh/frames/frame_0020.jpg` (t=01:00)
