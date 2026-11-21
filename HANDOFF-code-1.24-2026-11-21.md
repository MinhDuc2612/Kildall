# Handoff — finish code_1.24 (written 2026-11-21 by Claude, job 120663e4)

> **Status 2026-11-21 23:46: done.** Every item in section 4 is closed or recorded as a known limit with the user's OK (log in CLAUDE.md from 13:04). Nothing left for a next session.

Paste this to start the next session:

> Read `/Volumes/ES2TB/Kildall/HANDOFF-code-1.24-2026-11-21.md` and follow it. Finish code_1.24. Work until this
> session reaches 800k context, then write the next handoff the same way and stop.

## 1. Read first
1. `/Volumes/ES2TB/Kildall/CLAUDE.md`: standing rules at the top, then the log from "2026-11-06 — `code_1.24` gates at 2 × 32K" to the end.
2. `/Volumes/ES2TB/Kildall/code_1.24/README-1.24.md`.
3. `Orbiplan.md` → "THE FIT RULE" (v59) and `Researchhub/sample4/fitmodels-m4-24gb.md`.

## 2. Rules
- **Fit rule (user, 2026-11-21):** a model is used only if it writes ≥ 2 tok/s at all times on this Mac — worst case: longest context Kildall allows for it, 600 s soak, measured. Unmeasured = not usable.
- code_1.24 uses only models already on this Mac: cloud off, no downloads unless the user asks.
- **Commit or push code_1.24 only on the user's word.** The old `workstation` remote is retired; the vault pushes to `kildall` branch `workspace` after the full-history audit `code/.venv/bin/python code/.session/workspace-freeze-20261107/vault_audit.py HEAD <new-label>` passes.
- After each change run (with `.venv/bin/python` inside `code_1.24`): `test_local_lanes`, `test_local_media`, `test_routing`, `test_cloud`, `test_router_warmth`, `test_permissions`, `test_phase44`, `test_slot_isolation`, and `test_cli` (needs live models).
- Live tests need a quiet Mac: ports 8223/8224 free, no other model server, swap ≤ 3 GB. If the user's own `llama-server`s run, ask the user to quit them; never stop them yourself.
- Log every action in `CLAUDE.md` the moment it happens. Output style ELIS.

## 3. State at handoff (2026-11-21 ~10:45)
- code_1.24 last commit `8db691f`. **Uncommitted, tested:** `kildall.toml` — `flash_next` server block removed (fit rule); `test_routing.py` — live run now scores lane + category only (exit codes differ by lane in code_1.24). All 8 no-model tests exit 0. **`test_cli` and `test_routing --live` not run** (user's two `llama-server`s + opencode loaded, swap 14.7 of 16 GB).
- Machine: wired limit reads 22528 (boot daemon sets 20480) — note it, do not change it.

## 4. Done means (all of these)
1. `test_cli` 18/18 and the other 8 tests exit 0 on the final code.
2. `test_routing --live` lane 20/20 and category 20/20 (run in the background; > 560 s).
3. **Fit rule measured for every text model code_1.24 routes to:** Gemma 4 26B-A4B at 2 × 32K and Bolt E4B at 8K — worst-case tok/s ≥ 2 at full context through a 600 s soak. Record numbers in `README-1.24.md` and CLAUDE.md.
4. Open items closed, or recorded as accepted limits with the user's OK:
   - Bolt gives no pixel coordinates for pointing jobs.
   - Speech in is English only and hears "Kildall" as "Killdoll" (try a prompt/vocabulary hint for whisper-cli first).
   - A media job peaks at ~19 GB with swap near 16 GB while it runs.
5. `README-1.24.md` matches the measured state.
6. Committed and pushed on the user's word.

## 5. At 800k context
Stop new work. Write `HANDOFF-code-1.24-<date>.md` in this same shape (paste line, read list, rules, state, done list with what is left), log it in CLAUDE.md, and tell the user the paste line.
