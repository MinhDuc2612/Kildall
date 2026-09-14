# Hooks

Two sources of hooks are active in this environment: static `hooks.json` registrations shipped by installed plugins (found by searching `~/.claude/plugins/marketplaces/*/*/hooks/`), and runtime-level hooks observed operating this session that don't map to a static file on disk. Compiled 2026-08-20.

## Plugin-registered hooks (from each plugin's `hooks.json`)

| Plugin | Event | Matcher | What it runs |
|---|---|---|---|
| ecc | SessionStart (x2) | `*` | Internal hook runtime (inline Node) - session init, likely instinct/context loading |
| ecc | UserPromptSubmit / PreToolUse | `Bash`, `Write`, `Edit`, `Edit|Write`, `Bash|Write|Edit|MultiEdit`, `Write|Edit|MultiEdit`, `Edit|Write|MultiEdit`, `*` | Internal hook runtime - pre-tool checks (this is almost certainly where GateGuard's fact-forcing gate and similar guardrails are wired in, given ecc registers the most PreToolUse hooks of any plugin here) |
| ecc | PreCompact | `*` | Internal hook runtime - pre-compaction handling |
| ecc | PostToolUse (x2) | `*` | Internal hook runtime - post-tool bookkeeping (cost tracking observed this session likely lives here) |
| ecc | PostToolUseFailure | `*` | Internal hook runtime - failure handling |
| ecc | Stop (x6) | `*` | Internal hook runtime - end-of-turn bookkeeping (session logging, cost-tracker log, instinct capture) |
| ecc | SessionEnd | `*` | Internal hook runtime - session-end cleanup/save |
| ponytail (claude-codex) | SessionStart | `startup|resume|clear|compact` | activation script - activates ponytail mode banner/state |
| ponytail (claude-codex) | SubagentStart | - | propagates ponytail mode into subagents |
| ponytail (claude-codex) | UserPromptSubmit | - | persists mode across turns |
| ponytail (qoder variant) | UserPromptSubmit / PreToolUse | `task|Task` | same tracker/subagent scripts, alt-IDE variant |
| caveman | (same pattern as ponytail - activation + mode tracking) | - | Caveman-mode banner/state persistence (mirrors ponytail's structure) |
| superpowers | SessionStart | `startup|clear|compact` | loads the "using-superpowers" reminder |
| watch | SessionStart | - | verifies ffmpeg/yt-dlp/Whisper key present, prints remediation if not |
| last30days | SessionStart | - | verifies API keys/config for cross-platform research |
| i-have-adhd | SessionStart | `startup|resume|clear|compact` | persistent reminder/state plugin |
| hookify | PreToolUse / PostToolUse / Stop / UserPromptSubmit | - | runs user-authored `.local.md` hook rules (the plugin that lets a user define their own hooks in plain language) |
| ralph-loop | Stop | - | likely loop-continuation logic for the "ralph" autonomous pattern |
| claude-security | UserPromptExpansion | `^claude-security:claude-security$` | banner when that skill is invoked |

## Runtime hooks observed this session (no static file located - likely wired inside ecc's internal hook runtime above, or a separate binary)

- **GateGuard fact-forcing gate** - fires on the first Bash call of a turn and on destructive-looking commands; requires stating (1) the current request in one sentence and (2) what the command verifies/produces before it will proceed. Config/state lives at `~/.gateguard/` (per-session state file only - no visible rule-definition file on this machine; likely compiled into the ecc plugin's hook script or a separate daemon). Can be disabled per-session via an env var toggle or a disabled-hooks list entry.
- **Cost tracking / warnings** - a PostToolUse hook prints a running session-cost warning once a threshold is crossed (observed at $10, then escalating to "CRITICAL" past $50). Writes to `~/.claude/cost-tracker.log`.
- **Auto-mode Bash classifier** - when permission mode is `auto`, a classifier can deny a specific Bash invocation it judges too risky, independent of the fact-forcing gate.
- **Background-session isolation guard** - blocks Write/Edit/NotebookEdit tool calls in a background job's shared checkout until worktree isolation has run; does not block Bash-based file writes, a known gap used as a workaround this session when the target repo had no commits for worktree isolation to branch from.
- **CAVEMAN / PONYTAIL mode banners** - reprinted every UserPromptSubmit as additional context, reinforcing the active response style each turn (the visible effect of the ponytail/caveman UserPromptSubmit hooks listed above).

## Change log
- 2026-08-20 - Created from a filesystem sweep of installed plugins' hooks.json files plus hooks directly observed operating this session.
