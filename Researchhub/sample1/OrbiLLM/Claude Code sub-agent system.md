# Claude Code Sub-Agent System

Research on how Claude Code's sub-agent (formerly "Task tool") system actually works — definition methods, execution model, permissions, isolation, and orchestration options above single sub-agents. Compiled 2026-08-19 from Anthropic's official Claude Code docs plus independent technical writeups and one academic architecture paper.

---

## 1. What a sub-agent is

A sub-agent is a separate Claude instance the main ("lead") session spawns to handle a scoped task. Four properties define it:
- **Its own context window** — starts fresh, doesn't see the parent conversation's history, files already read, or skills already invoked.
- **Its own tool access** — can be restricted to a subset of what the parent has.
- **Its own system prompt** — lets you specialize behavior (a security-review sub-agent behaves differently from a feature-writer sub-agent).
- **Optionally its own model** — a cheap fast model can do triage while a stronger model does the hard work.

The core value proposition: the parent gets only the sub-agent's final summary, not the noise that produced it (forty file reads, a full test run, a documentation crawl). This keeps the main conversation's context clean for orchestration rather than flooded with intermediate detail.

## 2. Three ways to define a sub-agent

1. **Filesystem-based** — a Markdown file with YAML frontmatter in `.claude/agents/` (project-level) or `~/.claude/agents/` (user-level, available everywhere). Frontmatter fields include `name`, `description` (natural-language — this is what the lead reads to decide when to delegate), `tools`, and `model`. This is the persistent, reusable-specialist approach.
2. **Programmatic** — via the `agents` parameter when using the Claude Agent SDK directly in code. Programmatically defined agents take precedence over filesystem-based ones with the same name.
3. **CLI-defined** — passed as JSON at Claude Code launch. Exists only for that session, not persisted to disk — useful for quick tests or scripted automation.

A bare, undefined delegation call (just handing the built-in general-purpose type a prompt) is the ad-hoc option — inherits whatever the lead happens to be doing, no fixed system prompt. Use named definitions for repeat work, bare calls for one-offs.

## 3. Built-in sub-agent types

Claude Code ships three built-in types out of the box:
- **general-purpose** — all tools available; handles complex research, code modification, multi-step operations (exploration + modification together).
- **Explore** — read-only (no Write/Edit); file discovery and codebase search; as of Claude Code v2.1.198 it inherits the main conversation's model (capped at Opus on the Claude API) rather than always running on Haiku — you can still define a custom `Explore` agent with `model: haiku` to force the old cost-saving behavior.
- **Plan** — read-only; gathers context and designs an implementation strategy before presenting it, used in plan mode; doesn't touch files.

The lead routes to these automatically based on task characteristics and each type's description, though auto-selection is described as "imperfect in practice" by at least one independent source.

**A fourth, distinct pattern: forking.** A forked sub-agent inherits the parent's *full* conversation context instead of starting fresh — the opposite of the normal isolation model. Started via `/subtask`, or spawned automatically when "fork mode" is toggled on. This is the right choice when a task genuinely needs everything the parent already knows and you just want its noisy follow-up work kept out of the parent's context, versus a normal fresh sub-agent for a self-contained side task.

## 4. Invocation mechanism and naming history

Sub-agents are invoked through the **Agent tool**. This was called the **Task tool** prior to Claude Code v2.1.63, when it was renamed — old `Task(...)` references in settings and agent definitions still work as aliases, so both names remain valid to encounter in configs or documentation. A typical invocation carries a `subagent_type`, a short `description` (3-5 words, shown in the UI), a detailed `prompt` string, and optional `run_in_background` / `model` / `resume` parameters.

## 5. What a sub-agent actually inherits from the parent

A sub-agent's context window starts fresh but isn't empty — it reads the same `CLAUDE.md` files (project-level and user-level) at its own initialization. Critically, **it does not inherit the parent's interpretation state of that file** — each sub-agent interprets `CLAUDE.md` independently, which one source flags as a real risk of behavioral drift if the file contains ambiguous or context-dependent instructions. Beyond `CLAUDE.md`, the *only* content that crosses from parent to sub-agent is the literal prompt string passed to the Agent tool — so any file paths, prior error messages, or decisions the sub-agent needs have to be written directly into that prompt, not assumed to be "already known."

## 6. Execution model: foreground vs. background

As of 2026, sub-agents **run in the background by default** — the lead continues working and gets notified when a sub-agent finishes, rather than blocking. (Earlier versions, before v2.1.198, ran synchronously by default when `run_in_background` was omitted — this flipped.) A named background sub-agent shows up in the @-mention typeahead with live status, and you can message a specific one to resume it with its context intact, rather than starting a fresh one cold.

This split has a real permissions consequence, and it changed mid-2026: **foreground** sub-agents pass permission prompts through to the user for approval as normal. **Background** sub-agents, as of Claude Code v2.1.186, now surface their permission prompts in the main session too — tagged with which sub-agent is asking, and dismissing (Esc) denies just that one call without stopping the sub-agent entirely. Before v2.1.186, background sub-agents instead auto-denied any unapproved tool call silently, with no prompt or error surfaced — this older behavior was the source of most "why can't my sub-agent write files" confusion at the time, and is worth knowing about if working against an older Claude Code version. Either way, if a background sub-agent needs to ask a clarifying question rather than use a tool, that specifically still fails — `AskUserQuestion` isn't available to sub-agents at all regardless of foreground/background (see §7).

## 7. Tool and permission scoping

Two levers control what tools a sub-agent can reach:
- **`tools`** — an allowlist. Name specific tools and the sub-agent can use only those.
- **`disallowedTools`** — a denylist, removing named tools from whatever the sub-agent would otherwise inherit.

**The default, if you specify neither, is that a sub-agent inherits *all* tools available to the parent conversation — including MCP tools.** This is a genuine gotcha: omitting the `tools` field is not the safe/restrictive choice, it's the maximally permissive one. At least one production-practices source explicitly recommends the opposite default — start deny-all, allowlist only what a given sub-agent's job actually needs.

A fixed set of tools are **never available to sub-agents, even if explicitly listed**, because they depend on the parent conversation's live UI/session state — current list per Anthropic's docs: `AskUserQuestion`, `EndConversation`, `EnterPlanMode`, `ExitPlanMode` (unless the sub-agent's `permissionMode` is `plan`), `ScheduleWakeup`, `TaskOutput`, `WaitForMcpServers`, and `Workflow`. `Agent` itself is a special case, not a flat exclusion — it stays available to a sub-agent until that sub-agent hits the nesting depth limit (see §9), at which point further spawn attempts error rather than being invisible.

**Background sub-agents lose more than that.** A background sub-agent keeps all MCP tools but is limited to a specific, shorter list of built-ins: `Read`, `Grep`, `Glob`, `Bash`, `PowerShell`, `Edit`, `Write`, `NotebookEdit`, `WebFetch`, `WebSearch`, `TodoWrite`, `Skill`, `ToolSearch`, `EnterWorktree`, `ExitWorktree`, `Monitor`, `TaskStop`, `SendMessage`, and `Artifact` — everything outside that set is simply not present in a background sub-agent's session, regardless of what the `tools` field grants.

**Permission modes** a sub-agent can run under: `default` (standard prompting), `acceptEdits` (auto-accept file edits and common filesystem commands, Bash still prompts otherwise), `auto` (auto-approves tool calls with a background safety-classifier check instead of a human prompt — became the default mode for Pro/Max/Team plans on 2026-08-14 per Anthropic's own announcement), `dontAsk` (auto-deny all prompts — only pre-allowed tools function), `bypassPermissions` (skip all checks — cannot be overridden by the sub-agent itself), and `plan` (read-only exploration). The original version of this doc omitted `auto` mode entirely — a real gap given it's now the session default.

Session-level permission rules also support `Agent(AgentName)` syntax to allow or deny specific *named* sub-agents outright — e.g. adding `"deny": ["Agent(Explore)"]` disables the Explore type entirely for that project. Rule evaluation order is strict: **deny, then ask, then allow** — a broad deny rule cannot be overridden by a more specific allow rule that comes later.

## 8. Isolation modes

Beyond context-window isolation, Claude Code supports three levels of *filesystem* isolation for a sub-agent, per the architecture paper cited below:
- **In-process (default)** — shares the filesystem with the parent, but operates in an isolated conversation context.
- **Worktree** — creates a temporary git worktree, giving the sub-agent its own copy of the repository to modify without touching the parent's working tree. (This is the mechanism behind the `EnterWorktree`-style tooling for background-job isolation.)
- **Remote (internal-only)** — launches in a remote Claude Code Remote environment; always runs in the background.

## 9. Nesting — an evolving feature (corrected against current official docs)

Sources from different points in 2026 disagree, which reflects a real feature change over the year rather than a factual conflict: a March 2026 source states flatly that "sub-agents cannot spawn further sub-agents, which keeps the nesting manageable." By the time of this document's writing (Aug 19, 2026), nested sub-agents — agents spawning agents — were supported as a default-on behavior, not merely an available pattern: per Anthropic's own current docs, a sub-agent can spawn sub-agents of its own up to **three layers below the main conversation by default** (configurable), not the depth-5 figure originally cited here from a third-party source. Past that depth, the `Agent` tool remains listed as available to the sub-agent but errors instead of spawning, rather than being invisible outright.

## 10. Beyond a single sub-agent: the wider orchestration surface

Claude Code documentation frames sub-agents as one of four distinct ways to parallelize work, each suited to a different situation:

| Approach | What it gives you | Best for |
|---|---|---|
| **Sub-agents** | Delegated workers inside one session, own context, report a summary back | A side task would flood the main conversation with search results/logs/files you won't reference again |
| **Agent view** (`claude agents`) | One screen to dispatch and monitor several independent background sessions | Multiple genuinely independent tasks you want to hand off and check on periodically |
| **Agent teams** | Multiple coordinated sessions sharing a task list, with direct inter-agent messaging, managed by a lead | Work that needs teammates talking to each other, not just reporting to one parent |
| **Dynamic workflows** | A lead plans and fans out tens to hundreds of parallel sub-agents; a "Performance Outcomes" grader sends results back for revision against a rubric | Large-scale, structured fan-out work with built-in quality gating |

Sub-agents report only to the conversation that spawned them; agent-view sessions report only to the user; agent-team members can message each other directly and share a task list.

## 11. Safety architecture

Per an academic architecture paper analyzing Claude Code's design (arXiv:2604.14228), the safety model is **deny-first with human escalation**: deny rules override ask rules override allow rules, and any action the system doesn't recognize is escalated to the user rather than silently allowed. Multiple independent safety layers apply *in parallel* — permission rules, PreToolUse hooks, an optional auto-mode classifier, and shell sandboxing — so any single layer can block an action even if the others would have allowed it. Mechanically, sub-agent spawning (`AgentTool`) is dispatched through the same internal tool-factory as every other tool, re-entering the main query loop with an isolated context window and returning only a summary to the parent — sub-agent invocation isn't a structurally separate code path from normal tool use, just one that happens to spin up a nested Claude instance.

## 12. Practical takeaways / best practices (from independent sources)

- **Default to naming/scoping, not omission.** Explicitly set `tools` for any sub-agent doing anything beyond trivial read-only work — the unscoped default is full inheritance, the opposite of least-privilege.
- **Push single noisy operations into a sub-agent.** The single highest-return pattern cited across sources: any one operation that would produce a lot of output you won't need again (a broad search, a log trawl, a multi-file audit) is the canonical sub-agent use case.
- **Define reusable specialists for repeated worker patterns**, bare ad-hoc calls for one-offs.
- **Pair sub-agents with a `SubagentStop` hook** to enforce non-negotiable checks before the lead folds a result back into the main conversation.
- **Chain sub-agents in deterministic pipelines** for dependent work (analyst → architect → implementer → tester → security), or **run them in parallel** for independent specialization (UI, API, DB) — don't force one pattern where the other fits better.
- **Keep the orchestrator's own toolset narrow** — read and route, not do the work itself.
- **Structure research-sub-agent prompts with explicit output-format requirements** so results merge cleanly back into whatever the parent is assembling.
- **Watch for `CLAUDE.md` interpretation drift** across sub-agents given they don't inherit the parent's reading of it — ambiguous project instructions can be read differently by different sub-agents in the same session.

## Sources

- Claude Code Docs — Subagents in the SDK — https://code.claude.com/docs/en/agent-sdk/subagents
- Claude Code Docs — Create custom subagents — https://code.claude.com/docs/en/sub-agents
- Claude Code Docs — Run agents in parallel — https://code.claude.com/docs/en/agents
- Claude Code Docs — Configure permissions — https://code.claude.com/docs/en/permissions
- "Claude Code Agents & Subagents: What They Actually Unlock" — https://www.ksred.com/claude-code-agents-and-subagents-what-they-actually-unlock/
- "Claude Code subagents: the 2026 production playbook" — Totalum — https://www.totalum.app/blog/claude-code-subagents-totalum
- "The Task Tool: Claude Code's Agent Orchestration System" — https://dev.to/bhaidar/the-task-tool-claude-codes-agent-orchestration-system-4bf2
- "How to Use Claude Code Subagents to Parallelize Development" — https://zachwills.net/how-to-use-claude-code-subagents-to-parallelize-development/
- "Claude Code Subagents Architecture: Context Isolation and Parallel..." — https://claudecode.jp/en/news/engineer/subagents-in-claude-code
- "Claude Agent SDK Best Practices" — https://skywork.ai/blog/claude-agent-sdk-best-practices-ai-agents-2025/
- "Claude Code Subagents and Multi-Agent Orchestration Guide" — https://hidekazu-konishi.com/entry/claude_code_subagents_and_orchestration_guide.html
- "Claude Code Permission Rules Explained" — https://www.aifeaturedrop.com/2026/06/claude-code-permission-rules-explained.html
- subagent-tool-permissions-guide.md — skillsmith (GitHub) — https://github.com/smith-horn/skillsmith/blob/main/.claude/development/subagent-tool-permissions-guide.md
- "Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems" — arXiv:2604.14228 — https://arxiv.org/html/2604.14228

## Change log
- 2026-08-19 — Created. Researched directly via web search (not delegated to a fork, given narrower scope than the LLM survey).
- 2026-08-20 — Link/claim verification sweep against Anthropic's current official docs found real product drift since compilation: corrected the nesting depth (was cited as 5, actually 3 by default), the tools-unavailable-to-subagents list (added EndConversation/TaskOutput/Workflow), added the separate limited tool list background sub-agents get, and fixed the central §6 claim — background sub-agents now surface permission prompts as of v2.1.186 instead of silently auto-denying.
- 2026-08-27 — Final verification sweep. Re-checked every claim in this file against the live Claude Code docs (code.claude.com/docs/en/sub-agents, /agent-sdk/subagents, /permissions). Nesting-depth default (3), tools-never-available list, and the background-tool-restriction list all still match current docs exactly — no change needed there. Found and fixed two new instances of real product drift since the 2026-08-20 sweep: (1) §3's Explore-agent description said it "runs on a fast Haiku-class model by default" — as of Claude Code v2.1.198, Explore instead inherits the main conversation's model (capped at Opus on the Claude API), not Haiku by default. (2) §7's permission-modes list was missing `auto` mode entirely, which shipped and became the actual session default for Pro/Max/Team plans on 2026-08-14 (confirmed via Anthropic's own blog post) — a significant omission given it's now the default a reader would hit. All GitHub repos/issues, YouTube video titles/channels/upload-dates, and Anthropic blog posts cited across the other 9 files in this sweep were independently re-verified live and held up accurate; Reddit threads cited in several sibling files could not be re-verified this run (Reddit is unreachable via WebFetch/curl in this environment, consistent with prior sessions) — flagged here rather than assumed correct.
