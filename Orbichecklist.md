# Orbichecklist — Definition of Done

**v1 · 2026-09-05.** Orbi replaces Claude Code when this list is ticked. *(Product renamed Kildall 2026-09-27; see Orbiplan v31. History below keeps "Orbi".)*
**This is done-test #2.** Tests #1 and #3 are at the bottom.

---

# ⚡ ANSWER FIRST

| | |
|---|---|
| **Items** | **230** |
| **Done now** | **14** of 230 *(ticks for 4.1–4.4 not yet recorded)* |
| **The bar** | every P0 ticked, then the hard task, then one week with no Claude Code |
| **Owner** | you, via Codex |

**Priority:** **P0** = Orbi is unusable without it · **P1** = needed to replace Claude Code ·
**P2** = the "and more" beyond Claude Code.

---

## 1. Core loop — P0 *(Phase 1)*

- [ ] `orbi "..."` takes a prompt and streams a reply
- [ ] Ctrl-C cancels mid-generation without corrupting state
- [ ] Conversation history persists across restarts
- [ ] `orbi --continue` resumes the last session
- [ ] Piped input works (`cat f | orbi "summarise"`)
- [ ] Piped output is clean — no orbs, no colour codes
- [ ] Non-zero exit code on failure
- [ ] **Copy by reference (#57):** tools accept a source-span id; tool first-pass rises above 17/20 with frozen fixtures untouched
- [ ] **Repo map (#88):** the right files and symbols reach the context for coding tasks
- [ ] **Test-driven fix loop (#89):** run tests, fix, repeat until green or the cap; free-cloud escalation only after local failures
- [ ] **LoRA data collection (#90):** accepted diffs/answers stored locally with consent; never Claude/GPT outputs

## 2. Orbs — P1 *(Phase 1)*

- [ ] `○` idle `◐` thinking `◓` tool `◒` waiting `●` done `◉` error `◌` stalled
- [ ] One orb per running task
- [ ] Orb state survives a crash
- [ ] Auto-off when not a TTY

## 3. Memory — P0 *(Phase 1)*

- [ ] SQLite store, L0–L3 tiers
- [ ] Hybrid retrieval — BM25 + vector
- [ ] **Hard caps enforced: 12 items / 4,000 chars / 300 ms**
- [ ] **Global memory** — facts about you, all projects
- [ ] **Per-project memory** — scoped to the directory
- [ ] Global and project layers do not leak into each other
- [ ] Nightly backup, 14-day retention, markdown mirror
- [ ] Backups stored outside the code directory
- [ ] Survives delete-then-restore
- [ ] **20 recall pairs, 17+ correct**

## 4. Router — P0 *(Phase 2)*

- [ ] **Lane A picked from the 4 candidates** in `Orbimodels.md`. Leader: **Qwen3.8-27B + CMoE**
      (~17 GB, fits with room for Lane B). #2 `Qwen3.8-Flash-Next` (90 GB, no conversion, no quality loss)
- [ ] ⚠️ **Lane A measured above 15 tok/s** — unpublished for this shape on M4. **Test before all else**
- [ ] Lane A is **MoE, never dense** — a dense router forfeits the whole architecture
- [ ] Fallbacks ready in order: Gemma 4 26B-A4B, then Granite 4.1 8B
- [ ] Lane A model classifies a request into one of the 341 skills
- [ ] Skill maps to a lane, lane maps to a model
- [ ] `orbi ask --lane a` forces the fast path
- [ ] `orbi job submit` forces Lane C
- [ ] Lane A answers unless the task provably needs better
- [ ] Routing decision is logged and inspectable
- [ ] **18 of 20 varied requests route correctly**
- [ ] **Router prompt saved to disk (#62)** and reloaded after restarts; no cold route after a restart
- [ ] **Idle re-warm (#63)** of the router prefix after eviction

## 5. Files — P0 *(Phase 4)*

- [ ] Read a file, with line numbers
- [ ] Read a byte range of a large file
- [ ] Write a new file
- [ ] Edit by exact string replacement
- [ ] Refuse an edit whose target string is not unique
- [ ] Glob by pattern
- [ ] Grep with regex, file-type filter
- [ ] Read PDFs
- [ ] Read images
- [ ] Never write outside the allowed roots

## 6. Shell — P0 *(Phase 4)*

- [ ] Run a command, capture stdout and stderr
- [ ] Timeout with a configurable limit
- [ ] Background a long command
- [ ] Report the exit code honestly
- [ ] Working directory persists across calls
- [ ] **Refuse recursive delete, `sudo`, force-push — in code, not in the prompt**

## 7. Git — P1 *(Phase 4)*

- [ ] Status, diff, log without asking
- [ ] Commit only when asked, message written from the real diff
- [ ] Branch and switch
- [ ] Never push to main or master
- [ ] Never force-push
- [ ] Open a PR when asked

## 8. Skills — P1 *(Phase 4)*

- [ ] Load a named instruction pack on demand
- [ ] Skills discoverable from a directory
- [ ] A skill can declare which tools it needs
- [ ] `orbi skills` lists what is available
- [ ] Project skills override global ones

## 9. Hooks — P1 *(Phase 4)*

- [ ] Shell scripts fire before and after a tool call
- [ ] A hook can block a tool call
- [ ] Hook output reaches the model as feedback
- [ ] 🔑 **Every tool call constrained by a GBNF grammar**, not a prompt instruction — an invalid call
      must be unrepresentable, not merely unlikely
- [ ] **Phase 3's "never" tier is enforced by a hook, not a prompt**
- [ ] A failing hook fails safe — blocks, never silently allows

## 10. Subagents — P1 *(Phase 4)*

- [ ] Spawn a subagent with its own context
- [ ] **Shared mode** — one loaded model, interleaved contexts, near-zero extra RAM
- [ ] **Separate-process mode** — true parallelism, opt-in per task
- [ ] **Hard cap on separate processes, derived from free RAM**
- [ ] 🔑 **Continuous batching for shared mode** — `-np <slots>`. Without it "shared" means serialised:
      agent 2 waits for agent 1's whole answer. Size slots by KV-cache RAM, not agent count
- [ ] **p99 latency measured, not just throughput** — batching speeds the aggregate and slows any
      single answer, and Lane A also serves the interactive path
- [ ] Refuse to spawn when RAM would be exceeded
- [ ] Subagent results return to the parent
- [ ] A subagent cannot spawn another subagent
- [ ] **Verified review** (Ultrareview pattern): parallel reviewer subagents; every finding reproduced before it is reported — a 4.4 follow-up slice
- [ ] **Swarm orchestration**: a task split across a few Lane A subagents (RAM-capped), hardest step sent to Lane C
- [ ] **Code-built delegation prompts (#58):** the exact-once delegation smoke passes

## 11. MCP — P1 *(Phase 4)*

- [ ] Orbi is an MCP client
- [ ] Connect to a server over stdio
- [ ] Tool schemas load at startup
- [ ] A failed server degrades gracefully — never blocks startup
- [ ] ⚠️ Fix or drop `n8n` and `imessage` — both currently fail to connect

## 12. Permissions — P0 *(Phase 3)*

- [x] **Auto** tier: read, `ls`, `git status` — runs, logged
- [x] **Confirm** tier: write, edit, commit, install — asks, shows the exact diff
- [x] **Never** tier: refused in code
- [x] **Refuses a recursive delete with the system prompt removed entirely**
- [x] Permissive to you — no refusals on your own machine
- [x] Normally-aligned model, permissive prompt, **not abliterated**
- [x] Fetched web text is treated as data, never instructions
- [ ] ⏸ Guard model flags an injected page without obeying it — **deferred to Phase 4**: needs the web fetcher (Group 13) and Granite Guardian 4.1 8B, which is not on disk

## 13. Web and cloud — P1 *(Phase 4)*

- [ ] Search the web
- [ ] Fetch a URL and read it
- [ ] **Cloud used when necessary, not on request**
- [ ] **Rotates the 16 Cloudcall free-tier providers in order**
- [ ] Falls back to local when every free tier is exhausted, and says so
- [ ] **Never spends money.** Spend cap defaults to 0
- [ ] Per-provider rate limits tracked and respected
- [ ] 🔴 **Keys live only in the Keychain** — written on stdin, never argv; after a live run every key grepped across `.session/`, DB, logs and git = 0 *(4.5a)*
- [ ] 🔴 **Only allow-listed free model ids are called; HTTP 402 or a billing error disables that provider** *(4.5a)*
- [ ] 🔴 **Outbound secret scrub** on every cloud prompt, fetch URL and search query *(4.5a/b)*
- [ ] 🔴 **SSRF refused** — loopback, private, link-local, `.local`, and redirects to them *(4.5b)*
- [ ] 🔴 **Fetching a URL that came from neither you nor this task's search results needs Confirm** *(4.5b)*
- [ ] **Guard co-residency measured before it ships** — 10-min soak next to Lane A, 0 critical, 0 GPU OOM *(4.5b-0)*
- [ ] **Model Council**: Lane A + 2–3 free-tier models, a local chair shows agreement and disagreement — kept only if it beats Lane A on the eval
- [ ] **Deep research job** (`kildall research`, 4.5e): angles → search → fetch + guard → claims → 3-vote verify → cited report; queued, never blocks the terminal
- [ ] Every claim in a research report has a reachable source URL and quote; refuted and unverified claims listed separately
- [ ] 🔴 A failed or quota-limited vote counts as **unverified**, never merged as fact — fixture passes
- [ ] **NVIDIA NIM provider:** allow-list of live-verified free models; exact-model match for Lane C picks; $0

## 13C. Computer mode — P2 *(Phase 4C)*

**Research: `Researchhub/sample3/Orbicomputer.md`. Read its §4 first — it governs this group.**

- [ ] **CU-0 go/no-go: Lane A's 4 B active params can drive an accessibility tree at all.** ⚠️ Unmeasured, and there is a counter-signal — BrowserOS excludes local models from agent mode
- [ ] Reads the macOS accessibility tree (`AXUIElement`) and finds a named element
- [ ] Clicks and types through the tree, **with no vision model loaded**
- [ ] Browser control via `playwright-mcp`'s accessibility snapshot, not screenshots
- [ ] **Tries the tree first, every time.** Falls to pixels only on an empty or unusable tree
- [ ] **Logs which path ran** — tree or pixels — on every action
- [ ] **Opt-in and off by default.** Orbi does not have this capability until asked
- [ ] **Never runs unattended**
- [ ] **Every action clears the Phase 3 tiers BEFORE the input event is synthesised**, not after
- [ ] **Application allow-list** — drives only apps the user named
- [ ] **The pixel path always requires Confirm** — it cannot name what it is clicking
- [ ] 🔴 **Accessibility-tree text is data, never instructions** — a page can hide instructions in `aria-label` and the snapshot passes them through faithfully
- [ ] 🔴 **OCR'd screenshot text is data, never instructions** — injections hide in images invisibly to humans
- [ ] Refuses to act on a page carrying an injected instruction, in a real test fixture
- [ ] **Each bot gets its own computer** — a separate macOS user or a lightweight VM, never your desktop session; VM tool licences checked first. *(v36: default = separate macOS user; VM only for bots that browse untrusted sites or open unknown files; verify the 2-VM macOS limit and VM RAM)*
- [ ] **Gemma 4 vision (#59)** loaded with RAM measured next to Lane A, before 4C

## 14. Voice — P2 *(Phase 5)*

- [ ] **Speech in** — ASR transcribes what you say
- [ ] **Speech out** — Orbi reads answers aloud
- [ ] ~~Push-to-talk. No always-on mic~~ → superseded 2026-09-27: **local wake word**, audio never leaves the machine (Group 19)
- [ ] ~~ASR + TTS pair~~ → superseded 2026-09-27: **faster-whisper + Kokoro-82M**, not Qwen3-Omni (Group 19)
- [ ] Voice can be turned off entirely
- [ ] Falls back to text cleanly when audio hardware is missing

## 15. Media generation — P2 *(Phase 5)*

- [ ] Image generation
- [ ] Video generation
- [ ] 3D generation
- [ ] **All queued as jobs, never blocking the terminal**
- [ ] Progress is visible while queued
- [ ] Notifies on completion
- [ ] Output lands in a predictable directory

## 16. Lane C giants — P2 *(Phase 6 — ⏸ PARKED, drive 1+ month out)*

- [ ] External drive read/write speed measured before anything downloads
- [ ] Every ⚠ HF path resolved before a 4.9 TB download starts
- [ ] `kimi-k3-in-c` runs the 2.8 T tier
- [ ] Job queue runs detached and notifies
- [ ] **An overnight job beats Lane A on the same prompt — or Lane C is cut**

## 17. Hardware — P0 *(every phase that loads a model)*

**From `sample3/UHWmini.md`. Not a phase — a procedure that runs on every model load.**

- [ ] `uhwmini-setup.sh` run once and its output reviewed
- [x] ✅ `iogpu.wired_limit_mb` raised to 20480 (2026-09-06)
- [ ] ⚠️ **`check.sh` warns when the wired limit has reset** — it resets on every reboot
- [ ] Every model quantised **DWQ 4-bit**, not plain 4-bit (same size, 6-bit quality)
- [ ] DWQ build verified to load correctly before any benchmark
- [ ] KV cache quantised on every load — `-ctk q8_0 -ctv q8_0` (memory, not speed)
- [x] ✅ **Bounded prompt cache** — `--cache-ram 768 --ctx-checkpoints 3`. Took routing 15.29 s → ~0.97 s
      warm. 256 MiB and 512 MiB were tested and failed; do not shrink it
- [ ] `-fa on` set **and confirmed to have taken effect**
- [ ] `-lm mmap` used; **`--no-mmap` never** (deprecated)
- [ ] Context capped (default 32K) — the KV cache outgrows the model past ~100K tokens
- [ ] **Speculative decoding decided by measurement per platform** — on Metal it measured −11% to −28%, so off there; other GPUs enabled only if it wins (rule removed 2026-10-13)
- [ ] **Neural Engine never used** for token generation
- [ ] Every benchmark run **10 minutes minimum**, watching memory pressure
- [ ] **Hardware auto-fit (#51, Phase 7, v37)** — reads chip, RAM and memory bandwidth; derives quant, context, batch, cache and lane; propose → short gate → adopt. Passes on this Mac and on a smaller RAM budget (10-minute soak, zero critical samples, every frozen gate held). Required before the first paid client
- [ ] **Auto-expand upward only on an eval-harness (#13) win** — never on arithmetic alone
- [ ] **Per-slot context raised to 16K** (32K only if 16K passes) — KV/RSS/GPU per slot and prefill time measured; soak 0 critical, 0 GPU OOM
- [ ] Long prompts show progress and an estimated read time; every 4,096-token assumption is config-driven
- [ ] **4-bit KV cache** measured: ~2× context with no drop in recall, tools or routing
- [ ] **Document KV saved to disk:** a big file re-asked about reloads in seconds, keyed by file hash + model + flags
- [ ] **Retrieval for big files:** only relevant chunks enter the prompt, inside the memory caps
- [ ] **Map-reduce summaries** pass a fixed long-document test set with known answers
- [ ] **≥128K context on the 128 GB machine** with a compact-attention model, KV per token measured first

## 18. Operations — P1 *(throughout)*

- [ ] Secrets in macOS Keychain, never in config, DB, logs or backups
- [ ] `orbi budget set --monthly N`, default 0
- [ ] Warn at 80%, hard stop at 100%
- [ ] `orbi rollback` restores last known-good
- [ ] Log retention: L0 90 days, actions 180 days, backups 14 days
- [ ] Alarm if `orbi.db` passes 2 GB
- [ ] Weekly benchmark; **>10% throughput drop blocks `dev` → `stable`**
- [x] ✅ **Stale models replaced** — `granite-guardian` → **4.1**, `Molmo-72B` → **Molmo2 8B**.
      The other three audit entries are not used by Orbi
- [x] ✅ **Every model version-verified against its model card** (2026-09-06). Upgrades: Qwen-Image-2512,
      Qwen3-Reranker-4B, Harrier-27B embeddings; Qwen3-VL-235B dropped
- [ ] ⚠️ **Only Lane A goes on the internal disk** (it streams every request, needs the measured
      3.44 GB/s). **Lanes B and C go external.** Internal free: **93.3 GB, ~155 GB after emptying Trash**
- [x] `kildall nuke`, dry-run by default, must type `kildall` to confirm
- [ ] ⚠️ **`kildall nuke` deletes `~/Kildall/code/` and nothing else** — allow-list, not a deny-list.
      **Safety verified 2026-09-22: 14,918 paths listed, 0 outside `code/`.** Not fully ticked:
      3 outward `.venv/bin/python*` symlinks are refused, so `code/` is not completely removed.
      Fix: `os.unlink` the link itself (never touches the target), gated on the *link's own*
      location via `os.lstat`, not `realpath`
- [x] **Dry-run lists only paths under `~/Kildall/code/`** — if it lists anything else, the guard is wrong
- [x] `kildall nuke` cannot touch `Researchhub/`, the planning `.md` files, `Logo.png` or `.obsidian/`
- [ ] `code/` excluded from Obsidian indexing (Settings → Files & Links → Excluded files)
- [ ] `pip install -e ~/Kildall/code`, Python pinned `<3.13`
- [ ] Multi-session safe — SQLite WAL plus `busy_timeout`
- [ ] **Wired limit set at every boot (#52)** by a LaunchDaemon you install once with sudo
- [ ] **Permanent backup job (#53)** in `~/Library/LaunchAgents`; survives logout and pauses
- [ ] **Off-machine backup (#54)** of `kildall.db` to `KildallC`
- [ ] **Secret-scanner git hook (#55)** refuses commits containing a key
- [ ] **Platform layer** — keys, jobs, sandbox, OCR, computer mode, memory probe behind one interface; zero behaviour change on the Mac
- [ ] **Linux port** (any mainstream systemd distro; tested on Fedora + Ubuntu LTS) passes every gate on real hardware, incl. the Phase 3 sandbox tests
- [ ] **Windows via WSL2** passes every gate on real hardware; native Windows only if needed

## 19. Agentic OS — P2 *(Phase 9 — Kildall 100%)*

- [ ] **Laya-MLX answers typed decisions locally** (needs text gen? · category · command/question/note · interrupt?) and never decides a Never-tier action
- [ ] Laya becomes the first routing stage **only if it scores 20/20 category on the frozen fixture** — otherwise it pre-filters
- [ ] **Hermes Agent provides chat channels only**, calling Kildall's local endpoint; it has no shell, file or network tools
- [ ] 🔴 **A channel message asking for a recursive delete is refused by Kildall**, logged, nothing deleted
- [ ] **Voice in:** faster-whisper, English + Vietnamese; **voice out:** Kokoro (English) + a measured local Vietnamese TTS — no audio leaves the machine
- [ ] **Local wake word**; hard mute key; mic indicator always visible
- [ ] **End of speech → first audio under 1.5 s** on short commands, measured (else swap to mlx-whisper/whisper.cpp, recorded)
- [ ] Voice routes *"note that…"* to the vault and *"do…"* to Kildall
- [ ] **Obsidian second brain** with `raw/` · `wiki/` · `outputs/`, laid out and linked by Graphify
- [ ] 🔴 **A new, separate vault, not a git repo** — never in GitHub, Hugging Face or anything that leaves the machine
- [ ] Kildall retrieves vault context within the 12 items / 4,000 chars / 300 ms caps
- [ ] **Activity capture: everything** — apps, time, links, files, events, screen text, keystrokes → `raw/` → daily notes
- [ ] Capture exclusion list honoured (password managers, banking, private windows, Keychain prompts, key files); one command pauses it
- [ ] 🔴 **Raw keystroke log never sent to any cloud model**; keystroke and screen logs encrypted at rest; captured text treated as data, not instructions
- [ ] **Wallpaper dashboard** in a desktop-level window: RAM, pressure, swap, GPU, tok/s, lanes, cache hits, routing p50/p99, backups
- [ ] Dashboard lists every MCP connector (with failures), plugin, skill and agent, plus the skill audit (use count, success rate)
- [ ] **One-click skills** pass the same permission tiers — Confirm still asks
- [ ] **Skill mining chart** from all past sessions: task · desired output · proposed skill
- [ ] **Work interview** done, with blind spots called out
- [ ] Skills live at `.kildall/skills/<name>/SKILL.md` — trigger phrases in `description`; workflow, conventions, edge cases, ask-vs-infer, done
- [ ] **Every new skill is dry-run on a real example** and refined until it matches the manual result
- [ ] **Automations** scheduled and chained; **self-improving loops adopt a change only if it wins on the eval harness**
- [ ] **Google Workspace with full autonomy** (Gmail, Calendar, Drive, Docs) via MCP; every action logged; Never tier still blocked; OAuth in Keychain; the credential pasted 2026-09-27 revoked
- [ ] **Skill packs:** research · content creation · data workflows
- [ ] **Profiles per client** — theme, voice, wake word, instructions, skills; `kildall --profile <client>`
- [ ] 🔴 **Before the first paid client:** model licence audit, and per-client vault, memory, Workspace account and keys
- [ ] 🔴 **10-minute soak with the full stack resident, zero critical memory samples** — else voice and Laya load on demand
- [ ] **Voice command mode**: a spoken instruction edits the selected text or runs an action, English + Vietnamese
- [ ] **Local voice cloning** with mlx-audio (MIT), own voices only, RAM fit measured next to Lane A
- [ ] **Kildall Bots (9.11)**: `kildall-botd` daemon; named bots with their own memory and permission scopes, reachable by chat and dashboard
- [ ] **Kildall Bots desktop app (v36)**: the 9.6 web UI in a native window + menu-bar icon; creates, watches, pauses and approves bots; no tools of its own — everything routes to Kildall through `permissions.execute`
- [ ] 🔴 **The bot API is local-only and token-locked** — a request without the token, and one sent from a browser page, are both refused and logged; nothing runs
- [ ] **Shadow Twin (9.12):** learns style from prompts, edits, accepted/rejected outputs, own writing/repos and activity
- [ ] **User memory scope:** a per-user profile separate from global and project memory; local-only by default
- [ ] Shadow Twin controls: see, edit, delete, forget per item, pause, export
- [ ] **Twin gates:** blind A/B preference ≥ 70%; user A's profile never reaches user B; delete removes it everywhere

---

# THE OTHER TWO TESTS

## Test #1 — one week, no Claude Code *(the long-term bar)*

**You do a full week of real work in Orbi without opening Claude Code once.**
Not a demo week. Real work, on real repos, including at least one thing that goes wrong.

This is the bar that matters, and it is the last one to pass. A checklist can be fully ticked while
the tool is still miserable to use; a week cannot.

## Test #3 — one hard task, end to end *(run right after the checklist)*

**Orbi completes a multi-file refactor with the test suite passing, unassisted.**
No hints, no correcting it mid-way. It must find the files, make the change, run the tests, and fix
what it broke.

## Order

1. Tick every **P0** → Orbi is usable
2. Tick every **P1** → Orbi is a Claude Code replacement on paper
3. **Test #3**, the hard task → it works in practice
4. Tick **P2** → the "and more"
5. **Test #1**, the week → it has actually replaced Claude Code

---

## Change Log

- **2026-10-14** — 4 Shadow Twin items added to Group 19: **230 items**.
- **2026-10-13** — 4 items: NVIDIA provider, repo map, test-driven fix loop, LoRA data: **226 items**.
- **2026-10-13** — Speculative-decoding item reworded: a measurement per platform, not a ban.
- **2026-10-13** — 5 long-context items added to Group 17: **222 items**.
- **2026-10-12** — 3 cross-platform items added to Group 18: **217 items**.
- **2026-10-07** — 9 items for the early-scheduled improvements #52–#55, #57–#59, #62–#63: **214 items**.
- **2026-10-07** — 2 long-context items added to Group 17: **205 items**.
- **2026-10-06** — 3 items added to Group 13 for deep research (4.5e): **203 items**.
- **2026-10-04** — 6 safety items added to Group 13 from the Phase 4.5 design spec (Orbiplan v38): Keychain-only keys, free-model allow-list and billing stop, outbound secret scrub, SSRF refusal, Confirm for unseen URLs, guard co-residency soak: **200 items**.
- **2026-10-03** — 2 items added to Group 17 for hardware auto-fit and evidence-only auto-expand (#51, now a Phase 7 slice, Orbiplan v37): **194 items**.
- **2026-10-02** — 2 items added to Group 19 for the Kildall Bots desktop app (Orbiplan v36): the app itself and the local-only, token-locked bot API. Bot-computer item notes the v36 default (separate macOS user; VM only for risky bots): **192 items**.
- **2026-10-01** — 7 items added for the features adopted from `sample3/6aifeatures.md` (Groups 10, 13, 13C, 19): **190 items**. Kimi K2.6 recorded for later in the plan, not added.
- **2026-09-27** — Group 19 updated with the Phase 9 interview decisions (Hermes channels only, full capture with keystrokes kept local, English + Vietnamese voice, separate vault, Workspace full autonomy, paid-client prerequisites): **183 items**.
- **2026-09-27** — **Group 19, Agentic OS (Phase 9), added: 26 items → 182 total across 20 groups.** Voice items in Group 14 superseded by the local wake word and faster-whisper + Kokoro (Orbiplan v33). The done count is stale: Phases 4.1–4.3 passed but their items are not ticked yet.
- **2026-09-05 (v3)** — Lane A corrected from a dense model to **Qwen3.8-Flash-Next (MoE 180B/6B
  active)**, with an explicit item that Lane A must **never be dense**, and its **unmeasured tok/s
  flagged as test-before-all-else**. Added items for the **five known-stale models that must be
  replaced before Phase 3** — four are the guard and embedding models security depends on — and for the
  **155 GB vs 133 GB internal disk shortfall**. Now **126 items**.

- **2026-09-05 (v2)** — Lane A named (**Granite 4.1 8B**, fallback Qwen3.5-9B). Install path moved to
  **`~/Orbi/code`**, which put the code inside the research vault and forced the `orbi nuke` items to be
  rewritten as an **allow-list of one path plus a dry-run check**, rather than the old "never touches
  `~/Orbi/`" that is now impossible. Added an item to exclude `code/` from Obsidian indexing. Marked
  §16 Lane C **parked** — no drive for 1+ month. Now **120 items**.

- **2026-09-05 (v1)** — Created because done-test #2 requires a real feature checklist to exist.
  **156 items across 19 groups**, each tagged **P0** (unusable without), **P1** (needed for Claude Code
  parity) or **P2** (the "and more"), and each mapped to the phase that delivers it. Records the three
  agreed done-tests and the order they run in: P0 → P1 → the hard task → P2 → the week with no Claude
  Code. Carries forward the decisions made today — push-to-talk voice with no always-on mic, media
  generation queued rather than interactive, cloud used when necessary via rotating Cloudcall free
  tiers without ever spending, subagents in both shared and separate-process modes with a RAM-derived
  hard cap, and `orbi nuke` explicitly verified against the case-insensitive-volume collision that
  would otherwise let it delete the research vault.
