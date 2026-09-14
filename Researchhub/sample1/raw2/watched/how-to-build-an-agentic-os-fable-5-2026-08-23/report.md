---
source: https://www.instagram.com/reel/DamEcWuPvX0/
title: Video by raycfu
duration: 01:24
watched_at: 2026-08-23T21:51:28.697922+07:00
intent: research about it, identify the tool/project/technique being discussed, deep-research topic
hero_frames: [frame_0001.jpg, frame_0003.jpg, frame_0005.jpg, frame_0007.jpg, frame_0010.jpg]
transcript_source: local whisper.cpp (ggml-base.en.bin)
---

# Video by raycfu

## TL;DR

- Creator Rui Fu (@raycfu) pitches a "part 1" build guide for what he calls an **"Agentic OS"** — a self-managing pipeline of AI agents that runs unattended on a daily cron job, with escalating autonomy earned by a pass/fail track record.
- The named model throughout is **"Fable 5"** (API string shown on-screen: `claude-fable-5`) — this is NOT a publicly documented Anthropic model as of this research; treat it as either a rumored/leaked codename, a hypothetical/aspirational name used for teaching purposes, or product-specific branding by the creator. Could not be verified against Anthropic's official model list (see Sources/Verification notes below — web search and Perplexity were both unavailable/exhausted in this session).
- Architecture shown: a 4-role pipeline — **Scout** (cheap model, Qwen, read-only "did anything change?" check) → **Manager** (Fable 5, decides what must happen, writes a work order, never executes) → **Worker** (Sonnet, does the actual work) → **Inspector** (a fresh copy of Fable 5, reviews the Worker's output against the order).
- Key engineering details emphasized: treat HTTP 200 + `stop_reason == "refusal"` as a failure (not just non-200 exit codes), cap `max_tokens` at 64K, scale "effort" from low→max (extra-high reserved for loop tasks), and gate full autonomy behind a 95%-over-20-runs threshold per task type (drops back to supervised + email alert if success rate falls below 90%).
- A "goals directory" of self-written regression tests reruns daily so silent breakage in old work gets flagged automatically.
- This is lead-gen content: reel ends with "comment 'agent' and I'll send you the full guide," teasing a "part 2" — the video is a hook/teaser, not the full technical spec.

## Key moments

- **[00:00] Title card** — "How to build an Agentic OS using Fable 5, part 1" overlaid on talking-head shot (frame_0001.jpg).
- **[00:09] Model config screen** — mock UI "Config Inspector" showing a `model` field being typed as `cl...` (frame_0003.jpg).
- **[00:16] Model string revealed** — config shows `model = claude-fable-5`, `max_tokens = 65,536 (64K)`, and an effort slider low→medium→high→max→extrahigh with "extrahigh" gated behind a "Loop task" toggle (frame_0004.jpg).
- **[00:20-00:24] Refusal handling** — API mock shows `POST /v1/agentic/run` returning `200 OK, exit 0` but `"stop_reason": "refusal"` — the on-screen annotation reads "The refusal lives only in stop_reason," i.e. don't trust exit code alone (frame_0005/0006.jpg).
- **[00:27] The 4-role pipeline revealed** — Scout / Manager / Worker / Inspector cards under a `loop.sh` cron header (`cron 6 * * * *`, "AUTONOMOUS" toggle) (frame_0007.jpg).
- **[00:35] Scout role detail** — "A cheap model (Qwen) scouts first — cheap to ask 'did anything change?' every day," shown checking `metrics/signups.csv`, `content/blog/*`, `deploy.log` (frame_0008.jpg).
- **[00:40] Manager = Fable** — caption "if yes fable steps up as the manager"; annotation: "Fable is the manager: it writes exactly what must happen, but never does the work itself" (frame_0009.jpg).
- **[00:48] Report-card grading UI** — "Task grades over time," per-task-type letter grades (A, A+, A-, B+) with pass counts and autonomy status (Supervised/Autonomous) (frame_0010.jpg).
- **[00:59] Autonomy-loss email** — mock email "Deploy hotfix lost autonomy — Success rate fell to 88%, below the 90% floor. Reverted to check-ins automatically." (frame_0011.jpg).
- **[01:02-01:15] Goals directory / regression tests** — "What still works" dashboard showing daily proof-tests per feature (Checkout flow, Welcome email, Invoice export, etc.), with one shown flagged "BROKEN since today" (frame_0012/0013.jpg).
- **[01:15] CTA** — "I created a step-by-step guide... comment 'agent' and I'll send it to you. Follow for part 2" (frame_0014.jpg).

## Hook microscope (0-10s)

- Frames: 20 at 2 fps

0:00-0:06 opens directly on the title card ("How to build an Agentic OS using Fable 5, part 1") over the creator mid-gesture at his desk, no intro/greeting — straight demo-first hook. 0:06-0:09 cuts to a clean talking-head shot delivering the claim line ("most people don't realize Claude/Fable 5 can run for hours unattended, dispatch its own subagents, and do a week of work in one night") — an outsized-capability/contrarian-claim hook designed to stop the scroll on an AI/builder audience. By 0:09 it's already cutting to the first UI mockup, reinforcing "this is a real, buildable system" rather than talk. Pattern: **bold-capability-claim + demo-first**, with the specific named model ("Fable 5") functioning as a curiosity hook (a builder audience won't recognize the name and will watch to find out what it is).

## Editorial profile

- Shots: 14
- Cuts/min: 10.03
- Mean shot length: 5.98s
- Median shot length: 5.54s
- Talking-head ratio: n/a (opencv not installed)

Talking-head-to-camera intercut with mocked SaaS-dashboard-style UI overlays (config panels, API JSON, grade tables, emails) at ~10 cuts/min and ~6s mean shot length — a "build-in-public tutorial" pace: fast enough to hold attention, slow enough to actually read on-screen UI text.

## Quotable moments

- **[00:00]** "Most people don't realize that Claude/Fable 5 can run for hours unattended, dispatch its own subagents, and do a whole week of work in a single night."
- **[00:24]** "The refusal lives only in stop_reason" — i.e. a 200 OK / exit-0 response can still be a silent refusal.
- **[00:38-00:40]** "Fable accepts it as the manager — it does not do the actual work, but writes out exactly what needs to be changed."
- **[00:53]** "Once something passes 20 times at a 95% success rate, the system is allowed to do it completely on its own. But if the grade ever drops below 90%, the system loses that privilege and you get an email."
- **[01:12]** "The moment something you built three weeks ago quietly breaks, it flags it — this is how nothing you build will ever fall apart without you noticing."

## Entities mentioned

- People: [[rui-fu]] (@raycfu)
- Companies: (none named directly; "Fable 5" model string uses a `claude-` prefix on screen, implying an Anthropic/Claude association, unverified)
- Tools / products: [[fable-5]] (unverified model name), [[qwen]], [[claude-sonnet]], loop.sh (custom cron script name used in the demo, not a known public tool)
- Places: none

## Concepts surfaced

- **Agentic OS**: a self-managing, cron-triggered pipeline of AI agents with escalating autonomy, gated by measured task success rates rather than manual trust.
- **Scout/Manager/Worker/Inspector pattern**: split a cheap model (change detection) from a planning model (work orders) from an execution model (does the work) from a review model (checks the work) — cost and blast-radius control via role specialization.
- **stop_reason over exit code**: refusal detection must check the model's own stop reason field, since a refusal can still return HTTP 200 / exit 0.
- **Earned autonomy via report card**: per-task-type pass/fail grading; autonomy is granted at a 95%-over-20-runs threshold and revoked (with alerting) if it drops below 90%.
- **Goals directory / regression proofs**: self-written tests re-run daily so silent regressions in old work get caught and flagged automatically.

## Transcript

_Local whisper.cpp (ggml-base.en.bin) transcription of extracted audio. Model name transcribed as "Fable" / "CloudFable" is confirmed against on-screen text as "Fable 5" (frame_0001.jpg, frame_0004.jpg, frame_0009.jpg) — whisper mis-heard the preceding word as "Cloud" (likely "Claude")._

Most people don't realize that Claude/Fable 5 can run for hours unattended, dispatch its own subagents, and do a whole week of work in a single night. Here's how to build an actual Agentic OS using Fable 5.

Start by configuring the Agentic OS engine. The model string should be set to Fable 5, and make sure to set max tokens to 64K, so it caps the thinking plus the responses. Effort is always set to low to max, but never extra-high unless you're working with an agentic loop.

And here's the part most people miss. Refusals need to come back as HTTP 200. In this way, your scripts have to check for stop_reason / refusal and not just exit code.

Create a bash script called loop.sh and it runs on a cron drive every morning and runs your entire system. First use a cheap AI model like [Qwen] to look at your project, and ask if anything changed or needs attention. If yes, Fable steps up as the manager — it does not do the actual work, but writes out exactly what needs to be changed. Then you assign it to do actual work [with Sonnet], and a fresh copy of Fable that checks it like an inspector.

Next, build up the report card. Every task the system finishes gets logged as a pass or fail, and each type of task will earn its own grade over time. Once something passes 20 times at a 95% success rate, the system is then allowed to do it completely on its own. But if the grade ever drops below 90%, the system will lose that privilege and you get an email. So this way you never have to guess whether to trust your AI — the numbers will speak for you.

Build out a goals directory. The system writes out a simple test that proves it still works, and then it reruns one of those tests every single day. The moment something you built three weeks ago quietly breaks, it flags it. It tells you exactly what changed since it last worked. This is how nothing you build will ever fall apart without you noticing.

I created a step-by-step guide to build out this agent system with many more builds using Fable 5. Just comment "agent" and I'll send it to you. Follow for part 2 with the rest of the builds for the agentic OS system with Fable 5.

## All frames

_Total: 14. Hero frames flagged with star._

* `/private/tmp/watch-DamEcWuPvX0/frames/frame_0001.jpg` (t=00:00)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0002.jpg` (t=00:06)
* `/private/tmp/watch-DamEcWuPvX0/frames/frame_0003.jpg` (t=00:09)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0004.jpg` (t=00:16)
* `/private/tmp/watch-DamEcWuPvX0/frames/frame_0005.jpg` (t=00:20)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0006.jpg` (t=00:24)
* `/private/tmp/watch-DamEcWuPvX0/frames/frame_0007.jpg` (t=00:27)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0008.jpg` (t=00:35)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0009.jpg` (t=00:40)
* `/private/tmp/watch-DamEcWuPvX0/frames/frame_0010.jpg` (t=00:48)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0011.jpg` (t=00:59)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0012.jpg` (t=01:02)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0013.jpg` (t=01:10)
  `/private/tmp/watch-DamEcWuPvX0/frames/frame_0014.jpg` (t=01:15)
