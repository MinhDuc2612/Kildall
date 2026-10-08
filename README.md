# Kildall

![Kildall logo](assets/kildall-logo.png)

Kildall is a local terminal assistant with streaming replies, persistent sessions,
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
catalog, so sub-second routing is not guaranteed. B/C local execution remains unavailable.

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
kildall "Hello"
kildall ask "Explain SQLite WAL briefly"
kildall ask --lane a "Hello"
kildall ask --explain "Extract the table from this scanned invoice"
kildall job submit "Audit the architecture and propose a repair"
kildall --continue
printf 'Summarize this text' | kildall
```

From a fresh checkout on Apple Silicon, use Python 3.12:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
.venv/bin/python setup_kildall.py
```

Setup downloads and verifies the pinned runtime and two models (about 11.7 GB).
Do not run setup to enable other lanes: Phase 2 downloads no models.
Servers start locally on demand; `kildall --stop` releases them. The measured context
limit is 4,096 tokens. Generation uses a bounded native prefix cache
(`--cache-ram 768 --ctx-checkpoints 3`); embeddings keep caching disabled.
After updating from the old runtime flags, run `kildall --stop` before restarting.

The router's system/catalog prefix is saved under the git-ignored
`.session/router-prefix/`. Startup validates the full model, prompt, catalog and
server configuration before restoring it. The pinned b10809 runtime does not save
SWA checkpoints, so startup still rebuilds those with a prefix-only request before
becoming ready; disk restore alone does not remove that prefill cost. No user
request is saved in this file. An owned idle worker rebuilds a missing prefix and
cancels its HTTP request when foreground work arrives. An already executing Metal
batch cannot be preempted; pinned-slot cancellation is drained before reuse.
`kildall --stop` stops the maintenance worker and both model servers.

Memory uses SQLite WAL, BM25 and real semantic vectors, with hard limits of
12 items, 4,000 rendered characters and 300 ms. Personal facts are global;
project facts and sessions use the current directory. Ask Kildall to remember a
fact, or start a new prompt in a project to retrieve its context. Memory tools
are `remember` and `recall`. Phase4.1 adds file readers, approved write/edit and
confined commands; other model lanes remain unavailable.
For explicitly delimited exact facts, `remember` checks the source before saving,
retries a mismatch once with a diff, then fails if the copied text still differs.
This check recognizes explicit source delimiters, not arbitrary natural-language wording.
Ctrl-C saves partial state and exits 130. Orbs appear only on a terminal.

`kildall --backup` writes a verified SQLite snapshot and markdown mirror to
`../backups`, with 14-day retention. `kildall --restore PATH` restores a snapshot
after all active turns finish; it refuses to overwrite an active turn.
`kildall --schedule-backups` registers a 03:00 macOS job for the current login;
run it again after logging in. Its plist stays inside `.session/`.

After login, register backups with this exact command on this machine:

```sh
/Users/minhduc/Kildall/code/.venv/bin/kildall --schedule-backups
```

`./check.sh` verifies the loaded 03:00 backup job against its plist and reports
this command. It exits non-zero if registration is missing or mismatched, or
if `iogpu.wired_limit_mb` is 0; it prints the manual sysctl command in that case.

Run `.venv/bin/python test_memory.py` for deterministic memory checks.
`test_cli.py` and `test_recall.py` use the installed models and isolated test data;
start the local services with one `kildall` prompt before running the recall test.
Model files, databases, backups and runtime logs stay out of Git.

`ask` classifies the operational category and proposed catalog leaf in one call.
Requests too long for that compact catalog use the existing three-call hierarchy
within the4,096-token context; requests are never silently shortened. Neither path
verifies the proposed leaf match, and either can report an unmatched operation.
`ask --lane a` skips classification. Oversized requests can use the free cloud fallback below.
Legacy `kildall "..."` and `kildall --continue` retain their
direct Lane A behavior. `ask --continue` resumes with routing enabled.

The source contains **302 leaves, not 341**. All are represented with stable IDs,
source lines, historical evidence status and original/preferred model picks.
Named min-viable alternatives take priority. The source's 46 verification tags
are historical claims; other picks remain defaults, and unpicked leaves use
the companion plan's named defaults. Specialist operations use the explicit
`Orbimodels.md` job models where no leaf alternative exists, retaining the
catalog pick and explaining any difference in the log. Ordinary assistance stays on resident
Lane A. Specialist lane estimates are not RAM or quality qualifications.

Only Lane A is installed locally. With `[cloud].enabled = true`, unavailable B/C
choices and inputs exceeding local context may use the ordered free cloud providers.
An ordinary Lane A request stays local regardless of speed. With cloud disabled,
B/C choices retain the recorded `not installed` result; `job submit` records a
deferred Lane C intent. With cloud enabled, `job submit` attempts its cloud answer
synchronously. No background job scheduler or local Lane C model is installed.

Every routed request records its task, project/session, skill, lane, model,
reason, source status and outcome in SQLite `orbi_routes`. `succeeded` is true
only after an answer finishes, false on failure/cancellation/crash, and null for
unexecuted decisions/jobs. These records are included in the existing database
backups. No learning or reweighting uses the log.

`--explain` prints the reason and decision ID to stderr. Inspect a decision
later, from the same project directory, without starting any models:

```sh
kildall ask --decision DECISION_ID
```

Run `.venv/bin/python test_routing.py` for persistence and failure controls;
`test_routing.py --live` measures all 20 unchanged r-cases through the product
path using isolated data. It reports final lane accuracy separately from the
classifier's category accuracy.

## Free cloud and Keychain

```sh
kildall keys import                    # reads ~/.config/orbi/keys.env; keeps it
kildall keys import /path/to/keys.env
kildall keys check                     # Keychain availability, not an API charge/probe
kildall cloud enable llm7              # explicit reset of a billing lockout
```

Imports use login Keychain service `kildall`, variable names as accounts, stdin-only
credential writes and read-back hash verification. Output contains names/statuses.
Excluded Google/Gemini and Groq accounts are never imported or called. `keys check`
also remembers custom account names imported by this CLI, without storing values
in SQLite. Keys are read at call time; outgoing bodies and returned text are scrubbed.

Provider order and exact IDs live in `kildall.toml`: LLM7 (anonymous or free token),
anonymous OVH, then OpenRouter's exact free variants. A provider with no key is
inactive unless explicitly keyless. Anonymous LLM7 returned a live answer on2026-10-07,
despite current documentation requiring a token. This measured access may change.
Its free-token daily ceiling is applied conservatively to anonymous requests;
the anonymous service does not document that allowance.
Other researched providers remain unconfigured
until their exact free models and access requirements are established. Quotas and
data policies remain labelled `unverified`; an undocumented quota is not a promise
of unlimited use. No paid model fallback or automatic model discovery is enabled.

SQLite records per-provider attempts and token usage. Admission reserves usage
before sending, stopping at90% of documented daily limits (LLM7 uses rolling24h).
Uncertain requests retain conservative usage reservations. Token admission uses
a UTF-8 byte upper bound, so some long inputs may be rejected conservatively.
429/5xx/timeouts cause cooldown; Retry-After is honored. 401/403 invalidates that
credential until it changes. Billing errors disable the provider until the explicit
`cloud enable` command. Exhaustion reports `cloud exhausted — answering locally`.
If that input also exceeds Lane A's context, the existing context error remains
visible; the input is never silently shortened.

Cloud tool calls have no GBNF. They must match the same schema and enter
`permissions.execute`; malformed or credential-bearing calls are rejected without
repair. Confirm and Never tiers, hook boundaries and the computer-use guard hold.
Local regression runners explicitly disable cloud for their original fixtures;
`test_cloud.py` verifies cloud admission, rotation and executor boundaries with a
localhost mock server. No guard model, web fetcher or MCP is added in this slice.

Python is pinned to `>=3.12,<3.13`; `requirements.lock` pins the packages.
See [BASELINE.md](BASELINE.md) for the recorded measurements and
[../Kildallplan.md](../Kildallplan.md) for the local project plan (kept outside this repository).

## Permissions and Phase4.1 tools

Explicit actions run through a closed executor, without starting a model:

```sh
kildall tool read '{"path":"README.md"}'
kildall tool ls '{"path":"."}'
kildall tool git_status '{"path":"."}'
kildall tool write '{"path":"note.txt","content":"Hello\n"}'
kildall tool edit '{"path":"note.txt","old":"Hello","new":"Welcome"}'
kildall tool install '{"source":"artifact.bin","path":"installed.bin"}'
kildall tool commit '{"path":".","message":"Commit the reviewed staged changes"}'
kildall permissions
kildall permissions DECISION_ID
kildall nuke
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
kildall tool read_file '{"path":"README.md","start_line":1,"max_lines":20}'
kildall tool run_command '{"command":"sleep 5","timeout":10,"background":true}'
kildall tool shell_job '{"id":"JOB_ID"}'
```

Writes and Git operations are scoped to the hardcoded `~/Kildall/code/` root.
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
Enable this tool set with `kildall --git tools "Show Git status"`, or invoke a
typed action directly with `kildall tool`. `--git commit|push|pr` and `--skill NAME`
also enable it. Default requests retain the exact Phase4.1 tool definitions;
adding unrelated definitions caused a measured regression on a memory request.
Reads are Auto; mutations show their exact preview and require terminal confirmation.
Model commits, pushes and PRs additionally require explicit intent for that prompt:
`kildall --git commit "Review the staged diff and commit it"`. Repeat `--git` for
another requested action. Direct `kildall tool` invocation is also explicit intent.
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

`kildall skills` lists instruction packs without loading a model. Global packs live
in `code/skills/NAME/SKILL.md`; project packs in `PROJECT/.kildall/skills/NAME/SKILL.md`
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

Load on demand with `kildall --skill review "Review my changes"` or the model's
`load_skill` tool. Tool declarations are checked against available tools and never
grant permission. Packs are data, not executable scripts; symlinks, invalid
metadata and files over32KiB fail explicitly. `test_phase42.py` checks all11 items,
adversarial boundaries and the new tool grammars. PR transport is fixture-tested;
the test does not publish a live PR.

Opt in to shell hooks with `kildall --hooks PATH "Read this file"` or
`kildall tool --hooks PATH read_file '{"path":"README.md"}'`. The TOML file and
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
audit rows. Inspect them through `kildall permissions`.

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

`kildall nuke` is a dry-run. Deletion additionally requires `--delete` and typing
exactly `kildall` in the controlling terminal. Symlinks inside the root are listed
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

## Subagents

`kildall --agents shared "Ask two independent assistants to review these files"`
enables `spawn_agents` for that prompt. The usual twelve tools stay unchanged
without this option. Each child gets fresh context and its parent's tools and
Git intent; a child cannot delegate. Results return to the parent as tool data.
Tools run through the same executor, with confirmations in the parent's terminal.
Child memory writes stay in the parent project and child shell directories are
independent. `kildall permissions ID` shows the linked child decisions/results.

The shared configuration is three slots, each4096 tokens (`-np 3 -c 12288`),
with continuous batching, one global768MiB prefix cache and up to three checkpoints
per slot. Slot0 is reserved for routing. Answers, tools and direct generation use
workslot1; interactive turns serialize there. While the parent waits, up to two
shared children run concurrently on workslots1–2. Each slot has one owner, and
failed or cancelled requests drain before reuse. A batch refuses unavailable
slots or insufficient measured RAM headroom. See `BENCHMARKS.md` for the paired
routing, latency and memory-pressure results, including the failed two-slot option.

Separate model processes require `--agents separate` and an explicit `mode:
"separate"` child request. This machine's measured cap is **0**: the second model
loaded, but concurrent generation failed with Metal out-of-memory. No user/model
argument can bypass that failed certification. Re-measure before enabling it.
Process RSS includes mmap pages and is not a measure of additional physical RAM.

Ctrl-C interrupts child inference and reaps child shell jobs. A subsequent CLI
start recovers crashed child tasks and their recorded processes. Background jobs
created by children are confined to the batch lifetime; ordinary background shell
commands retain their existing behavior. Unfinished child jobs cancelled at cleanup
are returned to the parent and mark that child as failed. Run `test_phase44.py` for these controls;
latency, pressure, frozen quality gates and failed probes are in `BENCHMARKS.md`.

## Rename compatibility

The package and primary command are `kildall`. The `orbi` command and Python
module remain aliases for one release. Both commands share the same configuration
and database; `KILDALL_CONFIG` takes precedence over the legacy `ORBI_CONFIG`.
The vault lives at `~/Kildall`; SQLite table names and stored history retain their
existing names. Existing data and backups were copied and verified before cutover;
the originals remain available for recovery. Frozen benchmark text and model
prompts are unchanged except for the authorized vault path in project labels
and the write-tool description.

Licensed under the [MIT License](LICENSE).

Rename validation (2026-09-27): recall, abstention, category, lane and callable
JSON20/20; tools17/20 first-pass and20/20 post-retry; CLI18/18; hooks5/5.
All earlier controls and the health check pass. Recall requests differ only in
the vault path, verified by path-normalized comparison. See the retained results
and failures in [BENCHMARKS.md](BENCHMARKS.md).
