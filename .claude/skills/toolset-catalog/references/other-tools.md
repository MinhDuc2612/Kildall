# Other Tools (Non-Connector)

"Connectors" (Claude.ai's app-integration MCP servers — Gmail, Google Calendar, Google Drive, Slack, Notion, Figma, Canva, Adobe, ElevenLabs, Gamma, HyperFrames, Linear, Make, Motion, PayPal, Sentry, Supabase, Vercel, Wispr Flow, Zapier, higgsfield, v0, Clerk, Firecrawl, composio's app bridge) are deliberately excluded per instruction — those were removed from this environment earlier and this catalog doesn't re-introduce them as a reference. Compiled 2026-08-20.

## Research / dev-tool MCP servers (not app connectors)
- **Perplexity** (`mcp__perplexity__*`) — `perplexity_search` (ranked results, no synthesis), `perplexity_ask` (AI-answered with citations), `perplexity_research` (deep multi-source, slow), `perplexity_reason` (complex step-by-step analysis). Used extensively this session for all deep-research passes.
- **Context7** (claude.ai Context7) — fetches current library/framework/API documentation on demand; preferred over web search for docs questions, used even for well-known libraries since training data can be stale.
- **Chrome DevTools** (`mcp__plugin_ecc_chrome-devtools__*`) — full browser automation/inspection: navigate, click, fill forms, console/network inspection, screenshots, performance tracing, Lighthouse audits.
- **claude-in-chrome** (`mcp__claude-in-chrome__*`) — a second, separate browser-automation surface (tabs, computer-use style clicking, GIF recording, form input) — deferred/loaded on demand via ToolSearch.
- **n8n-docs** / **n8n-kapa** — n8n workflow-automation documentation lookup and support-bot search.
- **Composio** (`mcp__claude_ai_composio__*`) — meta-tool that discovers and executes actions across 500+ apps on demand (distinct from the fixed Connector list — this one searches/executes rather than being pre-wired per app).

## Session-level mechanisms worth knowing about
- **Output style** — currently `ELI5` (Simplified Technical English, short sentences, plain words), configurable via `/output-style` or `settings.local.json`'s `outputStyle` field. Composes with CAVEMAN/PONYTAIL mode (both active this session).
- **Deferred tools + ToolSearch** — many tools (most MCP servers, several built-ins like `WebSearch`/`WebFetch`/`Monitor`/`EnterPlanMode`) aren't loaded into context by default; `ToolSearch` fetches their full schema on demand by name or keyword. Keeps context lean until a specific tool is actually needed.
- **Memory system** (`~/.claude/projects/-Users-minhduc/memory/`) — persistent, file-based memory across sessions: user/feedback/project/reference memory types, indexed by `MEMORY.md`. Distinct from any single project's `CLAUDE.md`.
- **Workflow tool** — deterministic multi-agent orchestration (`pipeline()`, `parallel()`, `agent()` primitives) for structured fan-out work; requires explicit user opt-in ("ultracode" keyword, an "ultracode" session flag, or an explicit ask) — not used by default even when it would help.
- **Scheduling** (`schedule` skill, `CronCreate`/`CronList`/`CronDelete`) — recurring or one-time cloud-agent runs on a cron schedule, separate from the in-session `loop` skill (which self-paces or runs on a fixed interval within a live session).
- **Agent/fork mechanics** — see `agents.md` in this same catalog; `fork` subagents share the parent's context and prompt cache, other subagent types start cold.

## Change log
- 2026-08-20 — Created. Covers what's left after excluding the Connector app-integration list per instruction.
