---
name: toolset-catalog
description: Reference catalog of every skill, agent, and hook available in this Claude Code environment — session-loaded plugin skills, this machine's personal skill library, Agent tool subagent types, and hook registrations. Excludes Claude.ai Connectors (Gmail, Slack, Notion, Figma, etc.) by design. Use when asked what skills/agents/hooks/tools are available, or when deciding whether a capability already exists before building something new.
---

> ⚠️ **SAMPLE ONLY — REDO DURING THE BUILD.** This catalog is a point-in-time snapshot from a research
> pass, not build output. It is already known stale (its 2026-08-20 sweep recorded 57 of 61 personal
> skills as broken symlinks). Rebuild it against the live environment during the build.
> See `CLAUDE.md` → "The tooling is sample-stage."


# Toolset Catalog

A codified snapshot of the full Claude Code toolset on this machine, as of 2026-08-20 — everything except Claude.ai Connectors (the app-integration MCP servers like Gmail/Slack/Notion/Figma/Canva/etc., excluded per instruction since those were deliberately removed earlier). Four reference files, one per category:

- **`references/skills.md`** — every skill loaded into this session: built-ins plus plugin-provided skills (superpowers, ecc, caveman, marketing-skills, ui-ux-pro-max, taste-skill, and others), organized by source.
- **`references/agents.md`** — every subagent type the Agent tool can spawn in this session (custom `.claude/agents/*.md` definitions from plugins, plus the built-in Explore/Plan/general-purpose types).
- **`references/hooks.md`** — every hook registered by an installed plugin (event, matcher, what it does), plus the runtime-level hooks observed operating this session (GateGuard fact-forcing, cost tracking, the auto-mode Bash classifier) that don't have a static JSON file to point to.
- **`references/personal-skills.md`** — the machine-wide `~/.claude/skills/` library (separate from what's plugin-loaded into a session): honest finding is that only 3 of its 61 entries are currently functional; the other 57 are dangling symlinks to a "gstack" package that isn't installed on this machine.
- **`references/other-tools.md`** — non-Connector MCP tool groups (Perplexity, Chrome DevTools, Context7, n8n docs, Composio) and session-level mechanisms worth knowing about (output style, memory system, deferred-tool loading, Workflow orchestration, scheduling).

**What "codify" means here:** this is a catalog of what exists and what it's for, not a reproduction of every skill's full instructions — most entries are name + one-line purpose, which is enough to know a capability exists and route to it. Where something notable was found while compiling this (the broken personal-skills symlinks, in particular), it's called out rather than smoothed over.

**This snapshot will go stale.** Plugins update, personal skills get added/removed, hook configs change. Treat this as a point-in-time reference, not a live index — re-run the discovery pass (`find`/`ls` over `~/.claude/skills`, `~/.claude/plugins/marketplaces/*/`, and the session's own skill/agent listings) before trusting it for anything load-bearing.

## Change log
- 2026-08-20 — Created. Full sweep of session skills, session agents, plugin hooks, personal `~/.claude/skills`, and non-Connector MCP tools.
