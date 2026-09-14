# Coding agent CLI + notes vault voice command center

## TL;DR

- Source video: [Chase AI — "This Claude Code x Obsidian Agentic OS Will Be The New Meta"](https://www.youtube.com/watch?v=njHuj8OxIVI), YouTube, 24:17, published 2026-08-15, watched in full 2026-08-23 (80 scene-change frames + native captions, via `/watch`).
- The video is a hands-on build tutorial, not a product pitch: it shows a **personal coding-agent-CLI "OS"** built from four real, independently-verifiable pieces — (1) a custom notes-vault-app community plugin (built by the coding agent CLI itself) acting as a visual "command center" dashboard, (2) a day-to-day-task-to-skill-to-automation pipeline, (3) a Karpathy-style `raw/wiki/output` Markdown vault as a navigation "map" for the coding agent (explicitly *not* memory/graph-RAG), and (4) a fully local voice-control layer (local speech-to-text engine → small, fast routing model → 3-tier command dispatch → local text-to-speech engine).
- This is squarely an **agentic-OS build video** — the presenter frames it as "your entire Claude OS" and is explicit that the dashboard is cosmetic without the skills/automations backbone already in place ("this becomes a visual spectacle if we don't have this foundation").
- A closely related file already exists in this vault, [`Claude Code agentic OS.md`](Claude%20Code%20agentic%20OS.md), built from a *different* primary source (an Instagram reel by Gennaro Santoro) that cites this same Chase AI video as corroborating evidence of a wider trend. This file is the deep technical breakdown of that specific video (full watch, frame-by-frame, voice architecture) that the other file only had via last30days evidence snippets — treat the two as complementary, not duplicate.
- last30days research (30-day window, 2026-07-24 → 2026-08-23) found this exact video already generating downstream reaction: a GitHub issue in an unrelated project explicitly benchmarks itself against it, and Reddit/HN carry live debate over whether a notes vault app is even the right "memory" tool for this pattern.

## What it is

A 24-minute YouTube tutorial by creator "Chase AI" (channel tied to `chaseai.io` and the "Chase AI Plus" paid community/masterclass) walking through his personal setup that combines:

1. **A self-built notes-vault-app plugin** ("Command Center", labeled "AGENTIC OS" on screen) — a dashboard showing a big headline metric, token usage, social-media metrics, a Google-Calendar-pulled schedule/task breakdown, morning headlines, and clickable skill/automation buttons, with tabs for deeper reports (research, audience analytics).
2. **A skills-and-automations backbone** — the presenter's actual day-to-day coding-agent-CLI workflows (research pipelines, social monitoring, etc.) codified as reusable agent skills, promoted to scheduled automations only once proven manually.
3. **A notes-vault-app "memory" layer** — explicitly modeled on Andrej Karpathy's viral April 2026 tweet (~22M views) about using a Markdown vault as the coding agent's navigation structure: `raw/` (unsynthesized findings), `wiki/` (synthesized articles), `output/` (deliverables), each level carrying a master `index.md` as a table of contents.
4. **A fully local voice layer** — described as inspired by other AI assistants' voice-mode features, letting the presenter talk to the coding agent both inside and outside the notes vault app.

The video is not selling a product directly — it's a workflow build-along, with a plug at the end for the presenter's paid "Chase AI Plus" community, which reportedly includes the exact packaged setup (voice pipeline, plugin, skill library).

## How it works technically

**UI / plugin layer.** The dashboard is a real, custom-built notes-vault-app community plugin — the presenter states plainly "this is just a custom Obsidian plugin that Claude code actually built for me," and later walks through the build process: describe the desired command center to the coding agent CLI in conversation, use **an AI design/mockup-generation tool** to generate 5+ distinct visual mockups from reference images (e.g., Pinterest dashboard screenshots), iterate on a favorite, export the winning mockup's code as a zip, and hand that to the coding agent CLI to build and self-install as a working notes-vault-app plugin. The community "Hot Reload" plugin (found via GitHub search, not the vault app's official plugin browser) is used as a dev-loop aid so plugin changes apply without restarting the notes vault app.

**Voice pipeline (fully local, per the on-screen architecture diagram at 09:28):**

```
mic audio
  → a local, open-source speech-to-text engine (STT)
  → transcribed text
  → a small, fast routing model (routing LLM — "smallest, cheapest, fastest"; swappable for any local model)
  → routes into one of 3 tiers:
       Tier 1 (skills)  — execute a named skill directly, no reasoning overhead
       Tier 2 (metrics) — answer from an already-generated report/metric, fast, no fresh research
       Tier 3 (headless agent run) — spin up a full headless coding-agent-CLI run for open-ended/deep tasks (slowest, catch-all)
  → text response
  → a local, open-source text-to-speech engine (TTS)
  → spoken reply
```

The voice layer works even when tabbed out of the notes vault app entirely (demonstrated live inside the AI assistant's desktop app), and Tier 3 can trigger genuinely long-running background work ("go ahead and start doing deep research on X, Y, and Z") that reports back once finished rather than blocking.

**Skills-to-automations workflow.** Three ways to discover what should become a skill: (1) a voice/text "stream of consciousness" describing daily work, which the coding agent CLI mines for codifiable tasks; (2) mining the coding agent CLI's own historical tool-call logs (30/60/90 days) for what the user *actually* does versus what they think they do; (3) both combined. A task becomes a skill first and is validated manually before being promoted to a scheduled, unattended automation — explicitly framed as a discipline against AI's non-determinism ("I tell it to do one thing 10 different times, it's going to go about it 10 different ways... if I can specify the way I want things done and an end state, we can turn that into a skill").

**Memory-as-map, not memory-as-recall.** The video is emphatic that the notes-vault-app layer is not what most people assume: "It's not really giving it more memory, it's giving it a map" and explicitly denies it functions like a graph-RAG system ("it's not like a graph rag at all, actually"). The value is purely navigational — a folder structure + `index.md` table-of-contents at every level lets the coding agent find the right file quickly at scale (the presenter frames this as mattering once a vault has thousands to millions of files, not for a handful), which cuts both token usage and lookup latency. Users who don't want the literal `raw/wiki/output` layout can instead just spell out their own vault's navigation logic directly in `CLAUDE.md`.

## Current community reception (last30days, 2026-07-24 → 2026-08-23)

Ran via the `last30days` skill on the topic "coding agent CLI + notes vault agentic OS command center." **WebSearch was exhausted for this session (200/200) before pre-flight handle/subreddit resolution could run**, so the engine ran with `--auto-resolve` and manually-supplied subreddits only (`ObsidianMD, ClaudeAI, LocalLLaMA, PromptEngineering`) — no dedicated web-article supplements were fetched this run. X/Twitter returned nothing (no auth configured this session) and the engine's own keyless web-grounding backend was unreachable this run ("Web unreachable: Keyless web search unavailable") — treat Web and X as **not covered**, not as "nothing being said," per the engine's own partial-coverage warning. Active sources: Reddit, YouTube, Hacker News, GitHub, Digg (5 sources, 22 evidence items, 2026-07-24 → 2026-08-23).

**This exact video is already being used as a reference point to beat, not just watched.** A GitHub issue in an unrelated open-source project (`surdy/notes-method`) opened an epic titled "[epic] Agentic-OS roadmap: gaps from the Claude OS pattern," explicitly "prompted by the 'Claude Code x Obsidian Agentic OS' walkthrough (Chase AI...)" and concluding the author's own tool, Notesmith, is "already ahead of that pattern" on the same three pillars the video names (memory layer, automation backbone, UI) — direct evidence the video is shaping how at least one other builder frames their own project, within about a day of publication.

**Whether a notes vault app itself is the right memory layer is actively contested**, in a thread not about this video specifically but about the identical underlying pattern. In r/ObsidianMD's "Using Claude in Obsidian - looking for feedback on task management, agents & skills," u/bestwardenplayer pushes back directly: "my two cents is that Obsidian as a project memory for LLMs is honestly an outdated solution by now, I feel that the Oh-My-Pi harness does local agent memory + RAG (while being human readable and porta[ble])." A second commenter, u/watabebrothers, is more favorable to the pattern itself: "This is a genuinely well-designed system - the checkbox → daily log → project brief → knowledge note trail is exactly the kind of thing that survives a tool disappearing."

**A second, independent creator published the same core pattern outside YouTube in the same window.** "Obsidian + Claude Code: The Setup I Use Every Day" reached Hacker News on 2026-08-19 — a personal build-log describing a similar notes-vault-app-as-coding-agent-workspace setup, suggesting this is a small but real convergence across creators rather than one video's idea.

**The underlying tool (the coding agent CLI) had a rockier couple of weeks in the same window**, which is relevant context for anyone building an "OS" on top of it: an HN-surfaced GitHub issue reported "Claude Code is leaking real email address as a User-Agent string in curl command" (38 points, 29 comments), while a viral r/ClaudeAI thread, "I let Claude Code trade stocks with my real money. Results:" (2,335 upvotes, 393 comments), shows people already pushing the coding agent into much higher-stakes autonomous territory than a personal dashboard — the same "is this substance or spectacle" tension the video itself raises about UI-first agentic-OS builds.

**Net read:** the "coding agent CLI + notes vault app = personal agentic OS" pattern from this video is a real, small, currently-forming trend (corroborated independently by at least one other HN build-log and reactive interest from at least one unrelated open-source project), but the specific "notes vault app as memory" design choice at its core is not community consensus — a competing local-agent-memory harness is being cited as arguably superior in the same 30-day window.

## Relationship to other Orbi OS docs

- [`Claude Code agentic OS.md`](Claude%20Code%20agentic%20OS.md) — covers the wider "coding agent CLI + notes vault app = agentic OS" creator-economy trend from a *different* primary source (an Instagram reel selling a productized "Agency OS" skill), citing this same Chase AI video as one of three corroborating creators (alongside RoboNuggets). Read that file for the commercial/marketing angle; read this file for the technical build breakdown of one specific, fully-watched implementation.
- [`Jarvis-style personal AI operating system (LiveKit voice agent + HUD).md`](Jarvis-style%20personal%20AI%20operating%20system%20%28LiveKit%20voice%20agent%20%2B%20HUD%29.md) — a different local-voice-plus-dashboard pattern, useful to compare the voice-pipeline design choices (this video's local-speech-to-text → routing-model → local-text-to-speech stack vs. that doc's LiveKit approach).

## Sources

- [YouTube — Chase AI: "This Claude Code x Obsidian Agentic OS Will Be The New Meta"](https://www.youtube.com/watch?v=njHuj8OxIVI) — primary source, watched in full 2026-08-23 (80 frames, native captions).
- [GitHub — surdy/notes-method issue #295, "[epic] Agentic-OS roadmap: gaps from the Claude OS pattern"](https://github.com/surdy/notes-method/issues/295) — 2026-08-16, explicitly references this video.
- [Hacker News — "Obsidian + Claude Code: The Setup I Use Every Day"](https://lukasvonkunhardt.com/obsidian-claude-code-setup/) — 2026-08-19, 3 pts.
- [Hacker News — "Claude Code is leaking real email address as a User-Agent string in curl command"](https://github.com/anthropics/claude-code/issues/78431) — 2026-08-11, 38 pts, 29 comments.
- [Reddit r/ObsidianMD — "Using Claude in Obsidian - looking for feedback on task management, agents & skills"](https://www.reddit.com/r/ObsidianMD/comments/1vk14rc/using_claude_in_obsidian_looking_for_feedback_on/) — 2026-08-09, 13 comments.
- [Reddit r/ClaudeAI — "I let Claude Code trade stocks with my real money. Results:"](https://www.reddit.com/r/ClaudeAI/comments/1voi341/i_let_claude_code_trade_stocks_with_my_real_money/) — 2026-08-14, 2,335 pts, 393 comments.
- last30days raw research file: `~/Documents/Last30Days/claude-code-obsidian-agentic-os-command-center-raw-v3.md`.
- Staged /watch report + hero frames: `raw/watched/this-claude-code-x-obsidian-agentic-os-will-be-the-new-meta-2026-08-23/` (this vault).

## Limitations / what wasn't verified

- WebSearch was exhausted for this session before last30days pre-flight resolution could run, so no dedicated X-handle targeting or web-article supplements were fetched. X/Twitter community sentiment and general web coverage are **not represented** in the community-reception section above.
- No speech-to-text API key was configured this session, so the `/watch` transcript came from YouTube's native captions (not local speech-to-text) — captions were complete and high quality for this video, so this had no material impact on accuracy here.
- The presenter's paid "Chase AI Plus" package (which reportedly includes the packaged voice setup and skill library) was not independently inspected — only what's shown/described in the free video is treated as verified.

## Change Log

- 2026-08-23 — Watched the full video via `/watch` (yt-dlp + native captions, 80 scene-change frames, hook microscope), filled and staged the report + hero frames to `raw/watched/this-claude-code-x-obsidian-agentic-os-will-be-the-new-meta-2026-08-23/` in this vault. Ran `last30days` on "coding agent CLI + notes vault agentic OS command center" (WebSearch budget was exhausted this session, so pre-flight handle/subreddit resolution and web supplements were skipped; engine ran with `--auto-resolve` plus manually-supplied subreddits on Reddit, YouTube, Hacker News, GitHub, Digg). Wrote this combined research file, cross-referenced against the pre-existing `Claude Code agentic OS.md` in this same folder to avoid duplicating that file's Instagram-reel-sourced content.
- 2026-08-25 — Verification sweep: fixed a misattribution in the TL;DR — this file credited the sibling reel to "Sempra Systems," but per the primary `/watch` report (`raw/watched/agentic-os-for-your-agency-claude-code-2026-08-23/report.md`) and the sibling file `Claude Code agentic OS.md`, "Sempra Systems" is the brand on the creator's cap, not the creator — the reel's actual creator is Gennaro Santoro (`gennaroautomates`). Corrected to name him. No other factual issues found; cross-checked GitHub issue #78431, issue #295 in `surdy/notes-method`, and the `lukasvonkunhardt.com` post — all live and matching cited dates/points.
