# Orbichecklist — Definition of Done

**v1 · 2026-09-05.** Orbi replaces Claude Code when this list is ticked.
**This is done-test #2.** Tests #1 and #3 are at the bottom.

---

# ⚡ ANSWER FIRST

| | |
|---|---|
| **Items** | **156** |
| **Done now** | **4** of 156 |
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

## 11. MCP — P1 *(Phase 4)*

- [ ] Orbi is an MCP client
- [ ] Connect to a server over stdio
- [ ] Tool schemas load at startup
- [ ] A failed server degrades gracefully — never blocks startup
- [ ] ⚠️ Fix or drop `n8n` and `imessage` — both currently fail to connect

## 12. Permissions — P0 *(Phase 3)*

- [ ] **Auto** tier: read, `ls`, `git status` — runs, logged
- [ ] **Confirm** tier: write, edit, commit, install — asks, shows the exact diff
- [ ] **Never** tier: refused in code
- [ ] **Refuses a recursive delete with the system prompt removed entirely**
- [ ] Permissive to you — no refusals on your own machine
- [ ] Normally-aligned model, permissive prompt, **not abliterated**
- [ ] Fetched web text is treated as data, never instructions
- [ ] Guard model flags an injected page without obeying it

## 13. Web and cloud — P1 *(Phase 4)*

- [ ] Search the web
- [ ] Fetch a URL and read it
- [ ] **Cloud used when necessary, not on request**
- [ ] **Rotates the 16 Cloudcall free-tier providers in order**
- [ ] Falls back to local when every free tier is exhausted, and says so
- [ ] **Never spends money.** Spend cap defaults to 0
- [ ] Per-provider rate limits tracked and respected

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

## 14. Voice — P2 *(Phase 5)*

- [ ] **Speech in** — ASR transcribes what you say
- [ ] **Speech out** — Orbi reads answers aloud
- [ ] **Push-to-talk. No always-on mic**
- [ ] Uses the ASR + TTS pair (~2.0 GB), not Qwen3-Omni, by default
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
- [ ] **Speculative decoding never enabled in llama.cpp on Metal** (−11% to −28%). MLX only
- [ ] **Neural Engine never used** for token generation
- [ ] Every benchmark run **10 minutes minimum**, watching memory pressure

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
- [ ] `orbi nuke`, dry-run by default, must type `orbi` to confirm
- [ ] **`orbi nuke` deletes `~/Orbi/code/` and nothing else** — allow-list, not a deny-list
- [ ] **Dry-run lists only paths under `~/Orbi/code/`** — if it lists anything else, the guard is wrong
- [ ] `orbi nuke` cannot touch `Researchhub/`, the planning `.md` files, `Logo.png` or `.obsidian/`
- [ ] `code/` excluded from Obsidian indexing (Settings → Files & Links → Excluded files)
- [ ] `pip install -e ~/Orbi/code`, Python pinned `<3.13`
- [ ] Multi-session safe — SQLite WAL plus `busy_timeout`

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
