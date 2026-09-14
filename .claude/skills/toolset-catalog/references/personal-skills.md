# Personal Skill Library (~/.claude/skills/)

This is separate from the session-loaded plugin skills in `skills.md` — it's the user's own machine-wide skill folder at `~/.claude/skills/`, available across all projects, not tied to any one plugin marketplace. Compiled 2026-08-20 from a direct filesystem sweep.

## Honest finding: 58 of 61 entries are non-functional

`~/.claude/skills/` lists 61 directories. Checking each one's `SKILL.md`:

- **3 are real, working skills** (see below).
- **57 are symlinks pointing to a missing package.** Every one of `autoplan`, `benchmark`, `benchmark-models`, `browse`, `canary`, `careful`, `codex`, `connect-chrome`, `context-restore`, `context-save`, `cso`, `design-consultation`, `design-html`, `design-review`, `design-shotgun`, `devex-review`, `diagram`, `document-generate`, `document-release`, `freeze`, `gstack-upgrade`, `guard`, `health`, `investigate`, `ios-clean`, `ios-design-review`, `ios-fix`, `ios-qa`, `ios-sync`, `land-and-deploy`, `landing-report`, `learn`, `make-pdf`, `office-hours`, `open-gstack-browser`, `pair-agent`, `plan-ceo-review`, `plan-design-review`, `plan-devex-review`, `plan-eng-review`, `plan-tune`, `qa`, `qa-only`, `retro`, `review`, `scrape`, `setup-browser-cookies`, `setup-deploy`, `setup-gbrain`, `ship`, `skillify`, `spec`, `sync-gbrain`, `unfreeze`, and `_gstack-command` has a `SKILL.md` that's a **symlink to `~/.claude/skills/gstack/<name>/SKILL.md`** — and `~/.claude/skills/gstack/` does not exist on this machine. These are dangling references to a toolkit (apparently named "gstack") that was never installed here, or was removed. Right now, none of these 57 named skills can actually load or run.
- **1 is an empty stub.** `learned` is a real directory but contains nothing — likely meant to hold accumulated learned-pattern files that haven't been written yet.

## The 3 that actually work

- **graphify** — turns any input (code, docs, papers, images, video) into a persistent knowledge graph with god nodes, community detection, and query/path/explain tools. Treat any question about a codebase/architecture as a graphify query first when `graphify-out/` exists.
- **pinokio** — discover, launch, and use apps/tools for the current task.
- **setup-pc** — installs the user's standard macOS dev stack (languages, databases, infra, cloud CLIs, editors) — also present as a session plugin skill (same content, dual-registered).

## What this means practically

If the user or a future session invokes any of the 57 broken-symlink skill names (e.g. `/browse`, `/qa`, `/scrape`, `/ios-clean`), it will fail to load — the fix is either installing/restoring whatever "gstack" package these were meant to come from, or removing the dead symlinks if that package is genuinely gone for good. This document doesn't fix that; it just surfaces it, since the user asked to codify what exists, not what's advertised to exist.

## Change log
- 2026-08-20 — Created from a direct filesystem sweep of `~/.claude/skills/`. Found and reported the broken-symlink issue rather than treating the directory listing at face value.
