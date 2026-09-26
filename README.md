# Orbi

Orbi is a local terminal assistant with streaming replies, persistent sessions,
and scoped memory. Phase 1 uses Gemma 4 26B-A4B UD-IQ3_S with Harrier embeddings.
The latest controlled IQ3 run measured 26.64 tok/s and recall 20/20; the earlier
29.33 tok/s result used the previous cache configuration. See [BENCHMARKS.md](BENCHMARKS.md).

The Lane A DWQ retest scored Gemma 18/20 and Granite 14/20 on exact tool arguments.
Gemma still needs retries for two first-pass errors. Phase 2 adds routing decisions
around this classifier; the serving model remains Gemma IQ3_S.
The CLI continues to use the Phase 1 IQ3_S checkpoint; full retest measurements and
startup memory warnings are recorded in [BENCHMARKS.md](BENCHMARKS.md).
The two Gemma failures change punctuation inside valid string arguments. A tool-schema
grammar can enforce structure; it does not guarantee the requested string is copied exactly.
The shared system prompt distinguishes exact text from request punctuation and
matches retrieved facts by meaning. The 2026-09-13 run scores recall 20/20;
all 20 separate checks with the answering fact removed correctly return `UNKNOWN`.
The 2026-09-14 run scores exact arguments 18/20 first-pass and 20/20 after one
retry per failed call. Both punctuation errors are corrected by the model on retry.
Regex feedback identifies the failed target and explains when a trailing wildcard
requires an extra character; emitted arguments are never repaired by code.
The top three semantic hits remain protected and greedy decoding is verified.

Phase 2 product routing validation on 2026-09-20: **20/20**. r17 has no matching
specific catalog leaf and retains formal reasoning/C. Recall and abstention were
**20/20** in the preceding regression run.
The installed IQ3 model measures tool arguments **17/20 first-pass, 20/20 after
three retries**. The separate DWQ benchmark retains **18/20 first-pass, 20/20
after two retries**. Historical IQ3 also scored18/20; keep each run and backend distinct.
Product routing overhead averages **5.057 seconds**, including five cache misses;
the15 cache hits average **0.888 seconds**. Longer replies can evict the cached
catalog, so sub-second routing is not guaranteed. B/C execution is unavailable.

Phase 3 permissions validated on 2026-09-22: prompt-independent refusals,
terminal-confirmed diffs and a scoped nuke dry-run. Recall, abstention, routing,
JSON/tool scores and all 18 CLI controls retain their baseline; `check.sh` exits 0.
See the permission commands and current installation limits below.

The controlled IQ4_XS comparison on 2026-09-20 improved tool arguments to
**18/20 first-pass, 20/20 post-retry** at **24.00 tok/s**, including a first-pass
t09 pass. However, recall regressed to **19/20** (recall-18 answered `UNKNOWN`
despite retrieving Imani Tran), so **IQ3 remains selected**. Abstention and
product routing stayed 20/20 for both. Their actual routing means were 5.055s
(IQ3) and 4.998s (IQ4). Both ten-minute runs recorded memory-pressure warnings;
neither passed the all-normal pressure criterion. No model or prompt changes
were made after this comparison, and both weights remain on disk.

The recall-only rerun on 2026-09-21 removed the project-path confound:
**IQ3 20/20, IQ4 19/20**, with all 20 complete requests and effective greedy
parameters identical. IQ4 again answered `UNKNOWN` on recall-18 despite retrieving
Imani Tran second. This confirms the measured recall regression; IQ3 stays selected.

On this Mac, activate the existing environment and run:

```sh
source .venv/bin/activate
./check.sh
orbi "Hello"
orbi ask "Explain SQLite WAL briefly"
orbi ask --lane a "Hello"
orbi ask --explain "Extract the table from this scanned invoice"
orbi job submit "Audit the architecture and propose a repair"
orbi --continue
printf 'Summarize this text' | orbi
```

From a fresh checkout on Apple Silicon, use Python 3.12:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python setup_orbi.py
```

Setup downloads and verifies the pinned runtime and two models (about 11.7 GB).
Do not run setup to enable other lanes: Phase 2 downloads no models.
Servers start locally on demand; `orbi --stop` releases them. The measured context
limit is 4,096 tokens. Generation uses a bounded native prefix cache
(`--cache-ram 768 --ctx-checkpoints 3`); embeddings keep caching disabled.
After updating from the old runtime flags, run `orbi --stop` before restarting.

Memory uses SQLite WAL, BM25 and real semantic vectors, with hard limits of
12 items, 4,000 rendered characters and 300 ms. Personal facts are global;
project facts and sessions use the current directory. Ask Orbi to remember a
fact, or start a new prompt in a project to retrieve its context. Memory tools
are `remember` and `recall`. Phase4.1 adds file readers, approved write/edit and
confined commands; other model lanes remain unavailable.
For explicitly delimited exact facts, `remember` checks the source before saving,
retries a mismatch once with a diff, then fails if the copied text still differs.
This check recognizes explicit source delimiters, not arbitrary natural-language wording.
Ctrl-C saves partial state and exits 130. Orbs appear only on a terminal.

`orbi --backup` writes a verified SQLite snapshot and markdown mirror to
`../backups`, with 14-day retention. `orbi --restore PATH` restores a snapshot
after all active turns finish; it refuses to overwrite an active turn.
`orbi --schedule-backups` registers a 03:00 macOS job for the current login;
run it again after logging in. Its plist stays inside `.session/`.

After login, register backups with this exact command on this machine:

```sh
/Users/minhduc/Orbi/code/.venv/bin/orbi --schedule-backups
```

`./check.sh` verifies the loaded 03:00 backup job against its plist and reports
this command. It exits non-zero if registration is missing or mismatched, or
if `iogpu.wired_limit_mb` is 0; it prints the manual sysctl command in that case.

Run `.venv/bin/python test_memory.py` for deterministic memory checks.
`test_cli.py` and `test_recall.py` use the installed models and isolated test data;
start the local services with one `orbi` prompt before running the recall test.
Model files, databases, backups and runtime logs stay out of Git.

`ask` classifies the operational category and proposed catalog leaf in one call.
Requests too long for that compact catalog use the existing three-call hierarchy
within the4,096-token context; requests are never silently shortened. Neither path
verifies the proposed leaf match, and either can report an unmatched operation.
`ask --lane a` skips classification. Oversized requests fail visibly.
Legacy `orbi "..."` and `orbi --continue` retain their
direct Lane A behavior. `ask --continue` resumes with routing enabled.

The source contains **302 leaves, not 341**. All are represented with stable IDs,
source lines, historical evidence status and original/preferred model picks.
Named min-viable alternatives take priority. The source's 46 verification tags
are historical claims; other picks remain defaults, and unpicked leaves use
the companion plan's named defaults. Specialist operations use the explicit
`Orbimodels.md` job models where no leaf alternative exists, retaining the
catalog pick and explaining any difference in the log. Ordinary assistance stays on resident
Lane A. Specialist lane estimates are not RAM or quality qualifications.

Only Lane A executes. B/C choices print `would route to <model> (Lane B) — not
installed` (or Lane C) and exit **3**, without executing or substituting another
model. `job submit` forces C and exits **0 once its deferred intent is saved**;
Lane C remains parked pending external storage. No background execution or
automatic completion is scheduled. A job ID is its decision ID.

Every routed request records its task, project/session, skill, lane, model,
reason, source status and outcome in SQLite `orbi_routes`. `succeeded` is true
only after Lane A finishes, false on failure/cancellation/crash, and null for
unexecuted decisions/jobs. These records are included in the existing database
backups. No learning or reweighting uses the log.

`--explain` prints the reason and decision ID to stderr. Inspect a decision
later, from the same project directory, without starting any models:

```sh
orbi ask --decision DECISION_ID
```

Run `.venv/bin/python test_routing.py` for persistence and failure controls;
`test_routing.py --live` measures all 20 unchanged r-cases through the product
path using isolated data. It reports final lane accuracy separately from the
classifier's category accuracy.

Python is pinned to `>=3.12,<3.13`; `requirements.lock` pins the packages.
See [BASELINE.md](BASELINE.md) for the recorded measurements and
[../Orbiplan.md](../Orbiplan.md) for the local project plan (kept outside this repository).

## Permissions and Phase4.1 tools

Explicit actions run through a closed executor, without starting a model:

```sh
orbi tool read '{"path":"README.md"}'
orbi tool ls '{"path":"."}'
orbi tool git_status '{"path":"."}'
orbi tool write '{"path":"note.txt","content":"Hello\n"}'
orbi tool edit '{"path":"note.txt","old":"Hello","new":"Welcome"}'
orbi tool install '{"source":"artifact.bin","path":"installed.bin"}'
orbi tool commit '{"path":".","message":"Commit the reviewed staged changes"}'
orbi permissions
orbi permissions DECISION_ID
orbi nuke
```

Read/list/status are Auto. Write/edit/commit/install require the exact preview
and `yes` from the controlling terminal; piped input cannot approve them.
Text previews include complete before/after strings, preserving missing final
newlines and escaping control characters; binary artifacts use exact base64.
Install copies one existing local artifact, without executing it. Package
managers, build hooks and arbitrary shell/interpreter execution are unavailable.
Commit applies the already-staged diff on an existing local branch; it disables
Git hooks, fsmonitor, signing and maintenance. Linked Git worktrees are unsupported.
`run_command` supports `echo`, `printf`, `true`, `false`, `sleep`, `ls`, `cat`,
`wc`, `pwd` and `cd`, with optional `timeout` (1–3600 seconds) and `background`.
`cd` persists per project. `shell_job` takes an `id` to inspect a background
result; jobs survive their calling CLI. Output is bounded and explicitly marks
truncation; non-UTF8 output includes base64. The `shell` alias retains its old
read/list/status forms and also uses the same closed command executor.
No shell syntax, interpreter or arbitrary executable is evaluated. A native
macOS sandbox denies writes, network and child execution. Recursive delete,
sudo, force-push and computer control remain refused in code.

File tools are `read_file` (numbered UTF-8), `read_bytes` (offset/length,
base64), `glob_files` (path/pattern), `grep_files` (path/regex pattern/optional
file_type), `read_pdf` (text pages) and `read_image` (decoded dimensions and
macOS Vision OCR). Image scene understanding and scanned-PDF OCR are unavailable.
Reads are bounded and report truncation; denied or failed reads are errors.

```sh
orbi tool read_file '{"path":"README.md","start_line":1,"max_lines":20}'
orbi tool run_command '{"command":"sleep 5","timeout":10,"background":true}'
orbi tool shell_job '{"id":"JOB_ID"}'
```

Writes and Git operations are scoped to the hardcoded `~/Orbi/code/` root.
Realpath containment and descriptor-based file operations reject escapes; parent
directories must already exist. The permission check has no content/topic filter.
Existing memory tools retain their behavior and now receive permission audit rows.
Every model tool call uses schema-derived GBNF on native completion after the
unchanged Gemma chat template is rendered. Unsupported schemas and incomplete
calls fail closed. Grammar enforces structure, not exact string content.
The measured frozen suite remains17/20 first-pass and20/20 after retry. Routing,
the X no-match fallback and existing memory-tool schemas remain unchanged.

Phase4.2 adds `git_read` (status/diff/log), `git_branch`, `git_switch`,
`git_commit`, `git_push` and `git_pr` through that same executor and grammar.
Enable this tool set with `orbi --git tools "Show Git status"`, or invoke a
typed action directly with `orbi tool`. `--git commit|push|pr` and `--skill NAME`
also enable it. Default requests retain the exact Phase4.1 tool definitions;
adding unrelated definitions caused a measured regression on a memory request.
Reads are Auto; mutations show their exact preview and require terminal confirmation.
Model commits, pushes and PRs additionally require explicit intent for that prompt:
`orbi --git commit "Review the staged diff and commit it"`. Repeat `--git` for
another requested action. Direct `orbi tool` invocation is also explicit intent.
Ordinary prompt or skill text cannot grant it. A model commit must read the staged
diff and submit its returned hash with a message derived from those changes.
Only already-staged changes are committed; local Git author name/email must exist.
Switching requires a clean worktree and supports regular-file trees, not symlink
or submodule trees; hidden assume-unchanged/skip-worktree index entries are refused.
Staged/tree diffs include exact gitlink summaries; submodule worktree diff is unavailable.
Linked worktrees and executable/redirecting Git configuration
are rejected. Push supports GitHub HTTPS (installed `gh` credentials) and in-root
bare origins without active hooks, redirected stores or symbolic branch refs.
The destination is one explicit feature branch;
main/master, force, mirror and arbitrary refspecs are refused. PR creation
uses the GitHub API after explicit push, so it cannot silently push or fork.

`orbi skills` lists instruction packs without loading a model. Global packs live
in `code/skills/NAME/SKILL.md`; project packs in `PROJECT/.orbi/skills/NAME/SKILL.md`
override the same global name. Names use lowercase letters, digits and hyphens.
Each file has YAML frontmatter followed by Markdown instructions:

```markdown
---
name: review
description: Review the current Git changes
tools: [git_read]
---
Read the diff and report concrete problems with file references.
```

Load on demand with `orbi --skill review "Review my changes"` or the model's
`load_skill` tool. Tool declarations are checked against available tools and never
grant permission. Packs are data, not executable scripts; symlinks, invalid
metadata and files over32KiB fail explicitly. `test_phase42.py` checks all11 items,
adversarial boundaries and the new tool grammars. PR transport is fixture-tested;
the test does not publish a live PR.

Opt in to shell hooks with `orbi --hooks PATH "Read this file"` or
`orbi tool --hooks PATH read_file '{"path":"README.md"}'`. The TOML file and
scripts must be regular files under `code/`; relative script paths use its directory:

```toml
before = ["before.sh"]
after = ["after.sh"]
timeout = 2
```

Scripts receive `$1` (before/after), `$2` (operation), and `$3` (JSON event with
arguments, decision ID, status and the post-call result). For example:

```sh
case "$2" in
  write|edit) printf '%s\n' 'Writes blocked by this hook'; exit 77 ;;
esac
printf '%s\n' 'Hook checked the action'
```

Exit0 allows the normal permission checks; any nonzero exit, crash, timeout or
truncated output blocks. Pre-hooks run before confirmation/execution. Post-hook
failure stops further calls and fails the task; it cannot undo an executed action
or turn a background job into a failed job. Action and hook outcomes have separate
audit rows. Inspect them through `orbi permissions`.

Hooks add no model tools. Each selected configuration includes an independent
Never shell veto, while the original code enforcement always remains active.
Scripts are snapshotted before the task; changing a file mid-task does not change
the selected hook. Shell control flow and `:`, `[`, `test`, `printf`, `echo`,
`read`, `true`, `false`, `exit`, `break`, `continue` are available. External
programs, child processes, eval/source, writes, network and computer APIs are
unavailable. Hooks cannot grant consent or change tool arguments. Their output
is escaped tool data, not instructions. Limits: four scripts per stage,16KiB per
file,1–10 seconds per script,4KiB per output stream,64KiB event. Run
`.venv/bin/python test_phase43.py` for the five hook controls and confinement checks.

`orbi_permissions` follows the routing log pattern, including rejected,
declined, failed, cancelled and interrupted decisions. Inspection is project
scoped. `web_data` accepts a `text` field and returns inert untrusted data;
there is no web fetcher or claim of model-level injection resistance yet.
All computer input and screen-capture actions are refused until Phase 4C replaces
this temporary guard with its tree-first routing and per-action tier checks.

`orbi nuke` is a dry-run. Deletion additionally requires `--delete` and typing
exactly `orbi` in the controlling terminal. Symlinks inside the root are listed
and unlinked as entries, including the three outward Python links; their targets
are never followed or deleted. The live dry-run lists zero paths outside code/.
No root override exists. Nuke validates its audit database before opening it;
its final audit is emitted to stdout because successful deletion removes the
local database too. Destructive tests run only against temporary trees.

Run `.venv/bin/python test_permissions.py` for the Phase 3 adversarial controls,
including an empty `SYSTEM_RULES`, symlink escapes, real PTY confirmation,
computer-action refusals and throwaway-tree deletion.

Phase4.1 checks: `test_phase41.py`, `test_tool_grammar.py`, `test_tool_runtime.py`,
`test_shell_lifecycle.py`, `test_image_reader.py` and `test_nuke.py`. Detailed
results and retained failures are in [BENCHMARKS.md](BENCHMARKS.md).
