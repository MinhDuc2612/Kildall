# Session Skills

Every skill loaded into this Claude Code session, grouped by source. Invoke via `/name` or the Skill tool with `name` (add the namespace prefix, e.g. `superpowers:brainstorming`, when one is shown). Compiled 2026-08-20.

## superpowers (process/workflow skills)
- **using-superpowers** — meta-skill: how/when to invoke other skills; loads first in most sessions.
- **brainstorming** — required before any creative/build work; explores intent before implementation.
- **dispatching-parallel-agents**, **subagent-driven-development** — patterns for fanning work out to subagents.
- **executing-plans**, **writing-plans** — turn a spec into a step-by-step plan, then execute it.
- **finishing-a-development-branch**, **using-git-worktrees** — branch/worktree hygiene.
- **receiving-code-review**, **requesting-code-review** — code review workflow, both directions.
- **systematic-debugging** — structured debugging process, used before "fix this bug" requests.
- **test-driven-development** — write tests first, then implement.
- **verification-before-completion** — don't claim done without checking.
- **writing-skills** — how to author a new skill.

## ecc (large multi-purpose plugin — largest skill count in this session)
Covers code review/build-fix/testing per language (go, rust, python, java, kotlin, swift, dart, cpp, csharp, php, fsharp) as paired `<lang>-build` / `<lang>-review` / `<lang>-test` skills; framework-specific variants (django, fastapi, springboot, quarkus, react, vue, flutter); orchestration skills (`orch-add-feature`, `orch-build-mvp`, `orch-change-feature`, `orch-fix-defect`, `orch-refine-code`, `orch-review`, `orch-pipeline`); GAN-style generator/evaluator loops (`gan-build`, `gan-design`); session/instinct management (`learn`, `learn-eval`, `instinct-status/export/import`, `promote`, `prune`, `sessions`, `resume-session`, `save-session`); planning (`plan`, `plan-prd`, `plan-canvas`, `plan-orchestrate`); PR/git (`pr`, `prp-pr`, `prp-commit`, `review-pr`, `pr-test-analyzer`); security (`security-scan`, `security-review`); misc (`code-review`, `feature-dev`, `refactor-clean`, `test-coverage`, `update-codemaps`, `update-docs`, `deep-research`, `jira`, `harness-audit`, `harness-optimizer`, `ecc-guide`, `evolve`, `hookify`/`hookify-*`, `marketing-campaign`, `cost-report`, `pm2`, `project-init`, `projects`, `quality-gate`, `skill-create`, `skill-health`, `vue-review`, and ~150 topic-reference skills covering everything from `agentic-engineering` to `x-api` — too many to enumerate individually; search by keyword when needed (e.g. anything about databases, auth, deployment, a specific language pattern, or a specific domain like healthcare/finance/network-ops likely has an `ecc:*` skill).

## caveman (terse-response style + git helpers)
- **caveman** — switch terseness level (lite/full/ultra/wenyan).
- **caveman-init**, **caveman-commit**, **caveman-review**, **caveman-stats**, **caveman-compress**, **caveman-help**, **cavecrew** — git/commit/review helpers in the same terse style.

## ponytail (lazy-engineering style)
- **ponytail** — switch intensity level; enforces "does this need to exist" / reuse-first / shortest-diff discipline.
- **ponytail-audit**, **ponytail-debt**, **ponytail-gain**, **ponytail-review**, **ponytail-help** — audit/debt-tracking variants of the same discipline.

## marketing-skills (full marketing function, one skill per discipline)
ab-testing, ad-creative, ads, ai-seo, analytics, aso, churn-prevention, co-marketing, cold-email, community-marketing, competitor-profiling, competitors, content-strategy, copy-editing, copywriting, cro, customer-research, directory-submissions, emails, free-tools, image, influencer-marketing, launch, lead-magnets, marketing-council, marketing-ideas, marketing-loops, marketing-plan, marketing-psychology, offers, onboarding, paywalls, popups, pricing, product-marketing, programmatic-seo, prospecting, public-relations, referrals, revops, sales-enablement, schema, seo-audit, signup, site-architecture, sms, social, video.

## ui-ux-pro-max / taste-skill (design judgment)
- **banner-design**, **brand**, **design**, **design-system**, **slides**, **ui-styling**, **ui-ux-pro-max** (ui-ux-pro-max namespace)
- **brandkit**, **brutalist-skill**, **gpt-tasteskill**, **image-to-code-skill**, **imagegen-frontend-mobile**, **imagegen-frontend-web**, **minimalist-skill**, **output-skill**, **redesign-skill**, **soft-skill**, **stitch-skill**, **taste-skill**, **taste-skill-v1** (taste-skill namespace)

## Standalone / built-in-adjacent skills
- **graphify** — turns any input (code/docs/papers/images/video) into a persistent knowledge graph; query-first when `graphify-out/` exists.
- **pinokio** — discover/launch apps and tools for the current task.
- **setup-pc** — install the user's standard macOS dev stack.
- **design** — multi-artboard visual-design canvas published as an Artifact.
- **dataviz** — chart/graph/dashboard design system guidance, loaded before writing any visualization.
- **artifact-design**, **artifact-diagramming**, **artifact-capabilities** — Artifact authoring guidance (design fundamentals, diagramming mechanics, runtime capabilities like live data/state).
- **update-config** — configure the harness via settings.json (hooks, permissions, env vars).
- **keybindings-help** — customize `~/.claude/keybindings.json`.
- **code-review** — review current diff/PR/branch at a chosen effort level.
- **simplify** — reuse/simplification/efficiency pass on changed code (not bug-hunting).
- **fewer-permission-prompts** — scan transcripts, propose an allowlist to cut prompt friction.
- **loop** — run a prompt/command on a recurring interval.
- **schedule** — create/manage cron-scheduled cloud agents.
- **claude-api** — Claude API/Anthropic SDK reference (models, pricing, params, tool use, caching).
- **claude-in-chrome** — browser automation via the Chrome extension.
- **run** — launch/drive the current project's app to see a change working.
- **init** — (repo/project initialization; standard Claude Code skill)
- **security-review** — (security review workflow; standard Claude Code skill)
- **watch:watch** — download a video, extract frames + transcript, answer questions grounded in both.

## Other loaded plugins (single or few skills)
- **claude-hud:setup**, **claude-hud:configure** — status-line/HUD configuration.
- **humanizer:humanizer** — remove AI-writing tells from text (per Wikipedia's "Signs of AI writing" guide).
- **ralph-skills:prd**, **ralph-skills:ralph** — PRD authoring + the "ralph" autonomous-loop pattern.
- **andrej-karpathy-skills:karpathy-guidelines** — Karpathy's engineering-guideline reference.
- **last30days:last30days** — cross-platform (Reddit/HN/X/YouTube/Polymarket) topic research over the last 30 days.
- **imessage:access**, **imessage:configure** — iMessage integration setup/access.

## Change log
- 2026-08-20 — Created from this session's live skill listing.
