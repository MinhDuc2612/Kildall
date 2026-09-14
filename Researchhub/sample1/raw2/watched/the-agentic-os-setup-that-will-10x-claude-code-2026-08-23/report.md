---
source: https://www.youtube.com/watch?v=HRw-vP0j8OM
title: The Agentic OS Setup That Will 10x Claude Code
duration: 31:20
watched_at: 2026-08-23T22:00:00-00:00
intent: research about it, identify the tool/project/technique being discussed, deep-research topic
hero_frames: [f_001.jpg, f_005.jpg, f_010.jpg, f_015.jpg, f_020.jpg, f_025.jpg, f_030.jpg, f_033.jpg]
transcript_source: youtube-captions (en, auto-generated)
channel: Chase AI
upload_date: 2026-06-25
---

# The Agentic OS Setup That Will 10x Claude Code

## TL;DR

- The video (Chase AI / "Chase AI Plus" course creator) is a direct how-to on building a personal "Agentic OS" (AIOS) on top of Claude Code — exactly the "agentic OS building" topic this report was watched for.
- The claimed value isn't the visual dashboard — it's four stacked layers: (1) skill + loop engineering, (2) memory/state via a structured Obsidian vault, (3) a custom UI wrapping headless Claude Code, (4) distributing that UI to non-technical teammates/clients.
- The creator argues Levels 1-2 (skills/automation + memory/state) are "90% of the value" and can be done entirely inside the terminal with zero dashboard; Levels 3-4 (UI, distribution) are presented explicitly as "the cherry on top."
- Level 2's file structure is credited by name to Andrej Karpathy's viral (20M-view) tweet describing a `raw/ → wiki/ → outputs/` Obsidian folder scheme with an `index.md` map file at every level, explicitly labeled "not a real RAG system" ("RAG" in air quotes).
- Level 3 demo shows the dashboard is literally Claude Code running headless via `claude -p`, invoked from UI buttons/voice, writing back into the same Obsidian vault — not a separate agent framework.

## Key moments

- **[00:00] Cold open / thesis** — "If you don't know how to build your own agentic OS, then you are falling behind... not because you need some fancy dashboard... The value is everything under the hood": loop engineering, skill architecture, state management, second brain.
- **[00:48] Four-level framework introduced** — Level 1: skills + loop engineering (backbone). Level 2: memory + state. Level 3: interface/UI. Level 4: distribution. Levels 1-2 called "90% of the value."
- **[03:59] Sponsor break** — plug for the creator's own "Cloud Code Master Class" / Chase AI Plus paid community, which contains his exact AIOS build files.
- **[04:26] Level 1 detail — workflow audit** — three ways to surface skill candidates: (a) manual "I know what I do, turn it into a skill" via the skill-creator skill, (b) ask Claude Code to mine your last N sessions' tool calls for repeated tasks and propose skills (shown live, frame f_015: a "Repeated Tasks → Proposed Skills" table), (c) have Claude Code interview you in a stream-of-consciousness session to extract tasks.
- **[10:57] Skills → automation → loop engineering** — codified skill → cron-style automation ("routines" in Claude Desktop, name + instructions + schedule) → optional self-improvement loop layered on top (points to his separate prior "loop engineering" video, not covered in depth here).
- **[13:29] Level 2 — memory/state via Obsidian** — explicitly says Obsidian is not required; "even more so than Obsidian, it's the idea of file structures." A vault is just a designated folder; opening Claude Code inside it connects the two.
- **[16:47] Karpathy's Obsidian-RAG structure named on screen and verbally** — `raw/` (unstructured dump), `wiki/` (Claude-authored structured Wikipedia-style articles), `outputs/` (deliverables like slide decks), each level carrying an `index.md` so Claude Code always has "a map," reducing tokens/cost/latency. Says explicitly you don't have to follow this scheme — the map just has to make sense — and recommends a `CLAUDE.md` documenting vault conventions/navigation pattern (shown on screen, frame f_030).
- **[23:24] Level 3 — interface/UI demo** — a custom web-app command center ("V.A.U.L.T.", frame f_033: particle-sphere visualization, view/token-burn metrics, one-click buttons like "Inbox Brief" that trigger a skill) and an Obsidian-plugin equivalent ("command center" inside Obsidian itself). Confirms under the hood every button click is a **headless Claude Code invocation via `claude -p`**, and notes Anthropic's short-lived `claude -p`-billing controversy (briefly threatened to bill `-p` against API credits instead of the Max subscription, then walked it back).
- **[28:23] Level 4 — distribution** — web-app version is easy to hand off (GitHub repo/zip); the Obsidian version requires more hands-on setup per recipient. Framed as "raising the floor" for non-technical teammates/clients who won't touch a terminal.
- **[30:30] Close** — reiterates Levels 1-2 (skills, automation, memory/state, "second brain") are where "almost all the power" and "almost all your time" should go; 3-4 are cosmetic on top.

## Hook microscope (0-10s)

_Skipped: watch.py's own hook microscope requires the Whisper word-level pass (no Whisper API key configured in this environment) and the script's own video download failed with an HTTP 403; this report's frames/transcript were reconstructed manually via a direct yt-dlp + ffmpeg pass rather than the full pipeline._

Manual read of the opening 10s from frame f_001 + transcript: talking-head cold open, no B-roll, direct-to-camera claim-first hook ("If you don't know how to build your own agentic OS, then you are falling behind") immediately followed by a pre-emptive contrarian reframe ("But not for the reason you think... not because you need some fancy dashboard"). Pattern: **contrarian-claim hook that also defuses the obvious objection** before naming the real value ("everything under the hood") — classic YouTube-explainer retention structure, no visual gimmick needed since it's spoken entirely to camera.

## Editorial profile

- Shots: not measured (script's scene-change pass was bypassed; frames here are uniform 45s-interval samples, not true shot-boundary detection)
- Talking-head ratio: high — video alternates between direct-to-camera segments and full-screen screen-recording/Excalidraw-diagram segments with a small talking-head webcam overlay in the corner during demos.

One-line style fingerprint: educational/course-marketing YouTube explainer — direct-to-camera framework pitch, hand-drawn Excalidraw diagrams for the mental model, live terminal + custom-dashboard screen recording for proof, one mid-roll self-sponsor plug, low cut frequency (long unbroken talking segments, not fast-cut).

## Quotable moments

- [00:00] "If you don't know how to build your own agentic OS, then you are falling behind."
- [00:12] "The value is everything under the hood. Everything you can't see."
- [13:05] "Almost all the power, almost all of your time should be invested in these first two levels."
- [19:15] "The whole idea of this being a floor raising mechanism" (on giving non-technical teammates one-click access to Claude Code power via a custom UI).
- [22:52] "It's kind of like spinning them up on cloud code without actually spinning them up on cloud code."

## Entities mentioned

- People: [[andrej-karpathy]] (credited by name and on-screen tweet as the source of the raw/wiki/outputs Obsidian file-structure convention), the creator/narrator (channel "Chase AI", not otherwise named on screen)
- Companies: [[anthropic]] (referenced re: the `claude -p` billing-policy controversy)
- Tools / products: [[claude-code]] (shown on screen as v2.1.191, Opus 4.8, 1M context, Claude Max plan), [[obsidian]], [[claude-desktop]] ("routines" automation feature), `claude -p` (headless CLI invocation), skill-creator skill, ElevenLabs (mentioned only to say the demo's voice model is *not* using it — runs fully local instead)
- Places: none

## Concepts surfaced

- **Agentic OS (AIOS)**: this video's own coined/adopted term for a personal, customized system built on top of Claude Code — not a separate product, but a stack of conventions (skills, memory structure, optional UI, optional distribution).
- **Four-level AIOS framework**: Level 1 skill/loop engineering (backbone) → Level 2 memory/state (Obsidian or any structured file system) → Level 3 interface/UI (cosmetic wrapper) → Level 4 distribution (sharing the UI+skills bundle with non-technical users).
- **Workflow audit**: the practice of enumerating repeated day-to-day/week-to-week tasks (manually, by mining past session tool-calls, or via a Claude-led interview) before turning them into skills.
- **Karpathy's Obsidian "RAG"**: a `raw/` → `wiki/` → `outputs/` vault convention with an `index.md` map file at every folder level so an LLM agent can navigate a large vault cheaply; explicitly caveated in the video as not a real RAG system, just a navigable file map.
- **Loop engineering**: (referenced, not deep-dived — pointed to the creator's separate prior video) — closing the loop so an automation can see its own past runs' outcomes and self-improve future runs, tied to the same logged memory/state.
- **Headless Claude Code (`claude -p`)**: invoking Claude Code non-interactively (no visible terminal) from a button/voice command in a custom UI — the mechanism underlying every "level 3" dashboard button and "level 4" distributed tool in this video.
- **Floor-raising via UI**: framing a custom dashboard's real function as making Claude Code's skill/automation power usable by people who will never open a terminal, not as a feature in its own right.

## Transcript

_Source: youtube-captions (en, auto-generated), reconstructed via direct yt-dlp caption pull + manual VTT dedup (watch.py's own download step 403'd on this video; captions and video were fetched separately)._

Full timestamped transcript (916 lines) available at the working-directory path `/tmp/transcript_clean.txt` at watch time; key passages excerpted above under Key moments / Quotable moments. Not inlined in full here to keep the staged file a reasonable size.

## All frames

_Total: 42 uniform frames at 1-per-45s (script's scene-change detection was bypassed due to the manual re-download workaround). Hero frames flagged with star._

* `frames/f_001.jpg` (t=00:00) — talking-head cold open
* `frames/f_005.jpg` (t=03:00) — Excalidraw AIOS 4-level diagram
* `frames/f_010.jpg` (t=06:45) — Claude Code terminal (v2.1.191, Opus 4.8, "~\the vault")
* `frames/f_015.jpg` (t=10:30) — "Repeated Tasks → Proposed Skills" table from session-mining
* `frames/f_020.jpg` (t=14:15) — obsidian.md download page
* `frames/f_025.jpg` (t=18:00) — hand-drawn vault / raw / wiki diagram
* `frames/f_030.jpg` (t=21:45) — CLAUDE.md navigation-pattern file open in editor
* `frames/f_033.jpg` (t=24:45) — "V.A.U.L.T." custom dashboard (particle sphere, metrics, one-click skill buttons)
  (34 additional non-hero frames sampled at 45s intervals across the full 31:20 runtime, not individually listed)
