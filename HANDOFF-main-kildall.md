# Handoff — continue main Kildall (new session)

You are continuing the **Kildall** project. The previous session ran out of
room. Read `CLAUDE.md` first (it is the full project memory), then this prompt.

## What changed just now
- **Codex is retired — its API budget is exhausted.** You are now the ONLY
  builder AND reviewer. The old split ("Codex opens the PR and stops, Claude
  reviews and merges") no longer exists. You write the code, open the PR,
  review it yourself (re-read the full diff cold, run every gate, keep all
  failed-run evidence), and merge by ordinary fast-forward only when every gate
  passes. Never merge on a failed or unscored gate.

## "800k context window" means the SESSION budget, not a model context
- The user's phrase "to 800k context window" means **keep working in this new
  session until roughly 800k tokens are used, then hand off** — the same way the
  prior sessions were run. It does NOT mean giving a Kildall model an 800k-token
  window.
- An 800k-token model context is **physically impossible on this Mac** (M4,
  24 GB, ~20 GB usable for models). The plan already proved this: long-context
  work capped at 16K and still failed the memory soak, and real long context is
  deferred to the future 128 GB reward machine. If the user asks for a bigger
  model window, say so plainly and point at the reward-machine plan; do not chase
  it on this hardware.

## Rolling handoff — stop at ~800k and write the next prompt
- Work until this session reaches roughly **800k tokens**, then STOP.
- Before stopping, write a fresh handoff file for the next session (same shape as
  this one): what changed, current main/PR SHAs, the next unfinished job, and
  these same hard rules. Save it and send it to the user with SendUserFile.
- This repeats every session. Each session ends by handing the next one a correct,
  up-to-date prompt, so the project continues without losing state.

## Current repo state (verify before trusting — SHAs are from Codex's last report)
- Main code repo: `/Volumes/ES2TB/Kildall/code`, branch `main` = `c7c50ed`.
- Vault: `/Volumes/ES2TB/Kildall`, branch `workspace` = `a070538` (public repo
  `MinhDuc2612/Kildall`). This worktree `code_1.24` is the small-hardware test
  fork — leave it alone unless the user asks; main Kildall work happens in
  `/Volumes/ES2TB/Kildall/code`.
- **PR #13** (`repo-eval` branch, head `2a71126`, DRAFT): the #112 eval harness
  — 20 frozen bug tasks + verifier. Codex's last fix made git discovery stop at
  verifier-owned metadata. `test_repo_eval.py` passes. It is NOT frozen/merged.
- **PR #17** (`compaction` branch, head `0fa3f28`, DRAFT): the in-turn
  compaction fix (#48) — THE fix for the 0/20 frozen eval (the 4,096-token
  window fills with old tool steps). Focused tests 5/5. Its frozen #112 eval has
  NOT run yet: it keeps stopping at admission because swap was > 3 GB with Chrome
  and Wuthering Waves open.

## First job: finish PR #17, then PR #13
1. **Ask the user to quit Chrome and Wuthering Waves** before running gates (they
   push swap over the 3 GB admission limit). Confirm swap <= 3 GB and wired = 20480.
2. Review PR #17's diff cold. Then run its full gate set + both 20-task frozen
   #112 evaluations. The point is a real before/after number: the pre-#48
   baseline was 0/20. Keep every run's evidence, pass or fail.
3. If gates pass, merge PR #17 by ordinary fast-forward and verify the remote
   SHA + MERGED state. If a gate fails, fix it, re-run, do not merge.
4. Then review + merge PR #13 the same way (harness first makes sense, but #17 is
   the user-visible win, so prioritise #17's eval result).
5. After both, pick up the plan's next queued slice (read `Orbiplan.md` build
   order; the queued small slices come after 4.5a). Build one slice per PR.

## Hard rules (from CLAUDE.md — do not break)
- USB root `/Volumes/ES2TB/Kildall`. Run from the main code checkout.
- Admission before any model run: pressure normal, **swap <= 3 GB**, ports
  8123/8124 free (no LISTEN socket + SO_REUSEADDR bind), no other model process.
- Wired limit must read 20480 (user runs the sudo sysctl; never run sudo yourself).
- **Never push to `main` directly** — PRs only, ordinary fast-forward merge, no
  force, no rebase of main.
- **Full-history secret scan before every push** (the pre-commit secret-scanner
  hook stays on; never bypass it). Never push models, DBs, `backups/`,
  `.session/` evidence, or keys.
- **Never a paid API or paid cloud.** No sudo. Other Claude sessions share this
  Mac — never stop or change their processes, no broad pkill.
- Hooks stay on. If a hook or safety check blocks you, do not work around it.
- `kildall nuke` deletes only `/Volumes/ES2TB/Kildall/code` (allow-list of one).
- Pending CLAUDE.md log lines live in `CLAUDE-log-pending-*.md` in the
  `code_1.24` worktree; Codex used to fold them into CLAUDE.md on vault commits —
  now you must do that yourself on the next vault commit.

## Standing user style
- Output style ELIS + caveman (full): short, plain words, no filler. Code and
  commits written normally.
- Two options max on any decision, with your pick named first.
