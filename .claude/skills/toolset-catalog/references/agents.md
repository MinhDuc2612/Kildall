# Session Agent Types

Every subagent type the `Agent` tool can spawn in this session (`subagent_type` parameter). Compiled 2026-08-20.

## Built-in
- **claude** — catch-all default when no specific agent applies (all tools).
- **general-purpose** — complex research, code search, multi-step tasks (all tools).
- **Explore** — fast read-only search/discovery (all tools except write/edit/plan-exit).
- **Plan** — software-architect agent for implementation planning (read-only).
- **fork** (via `subagent_type: "fork"` on the Agent tool) — inherits the caller's full conversation context instead of starting fresh; always runs on the caller's model.
- **statusline-setup** — configures the status line (Read, Edit only).

## caveman namespace
- **cavecrew-builder** — surgical 1-2 file edits only; hard-refuses 3+ file scope.
- **cavecrew-investigator** — read-only code locator, returns compressed file:line tables.
- **cavecrew-reviewer** — terse severity-tagged diff/PR reviewer.

## claude-code-guide
- Answers questions about Claude Code itself, the Agent SDK, the Claude API, Claude Tag (Slack), and `claude plugin eval`.

## ecc namespace (largest set — one specialist per language/domain, roughly matching the ecc skill list)
Language build-resolvers and reviewers for: C++, C#, Dart/Flutter, Django/Python, F#, Go, HarmonyOS/ArkTS, Java (Spring Boot/Quarkus aware), Kotlin, PHP, PyTorch, React, Rust, Swift, TypeScript/JavaScript, Vue. Domain specialists: a11y-architect, agent-evaluator, architect, chief-of-staff, code-architect, code-explorer, code-simplifier, comment-analyzer, conversation-analyzer, database-reviewer, doc-updater, docs-lookup, e2e-runner, fastapi-reviewer, gan-evaluator/generator/planner, harness-optimizer, healthcare-reviewer, homelab-architect, loop-operator, marketing-agent, mle-reviewer, network-architect/config-reviewer/troubleshooter, opensource-forker/packager/sanitizer, performance-optimizer, planner, pr-test-analyzer, refactor-cleaner, security-reviewer, seo-specialist, silent-failure-hunter, spec-miner, tdd-guide, type-design-analyzer. (~70 total; search by domain keyword when picking one.)

## Change log
- 2026-08-20 — Created from this session's live agent listing.
