# Kildall-27b (branch `kildall-27b`)

One brain: **Swift-1.5-Qwen3.8-27B** drives every Kildall feature. No router, no catalog dispatch,
no Lanes B/C. Plan: `/Volumes/ES2TB/Kildall/Kildall27b.md`. This branch is never merged into main;
main fixes are merged into it from time to time.

## What differs from main

| Item | main | Kildall-27b |
|---|---|---|
| Folder (`CODE_ROOT`, nuke root, USB guard) | `/Volumes/ES2TB/Kildall/code` | `/Volumes/ES2TB/Kildall/code_27b` |
| Model | Gemma 4 26B-A4B IQ3_S | `/Volumes/ES2TB/AI-Models/Swift-1.5-Qwen3.8-27B-Q4_K_M/...gguf` |
| Ports (model / Harrier) | 8123 / 8124 | 8423 / 8424 |
| Slots | 3 (router 0, work 1-2) | 1 |
| Database | `kildall.db` | `kildall27b.db` |
| Backups | `~/Library/Application Support/Kildall/backups`, `local.kildall.backup` | `.../Kildall27b/backups`, `local.kildall27b.backup`, logs `~/Library/Logs/Kildall27b` |
| Router | `routing.py`, `skill_catalog.py`, `router_warmth.py` | removed; `kildall ask` is a plain prompt; `job submit`, `--explain`, `--lane`, `--decision` removed |
| Cloud | per-lane picker + exact catalog model | fixed backup only when the request does not fit the 27B |
| Runtime | b10809 | b10809 (shared from `code/.tools` by a `.tools` link); slice 27b-1 measures Homebrew 12359 |

Harrier and the b10809 runtime are read from main's folder (read-only use).

## Slice 27b-0 gates (2026-11-22, launchd `ProcessType=Interactive`)

| Gate | Result |
|---|---|
| 27 standing controls (main's 28 minus the two router tests, plus `test_tool_result_context`) | 27/27 pass |
| `check.sh` | exit 0 (wired 20480, boot daemon, `local.kildall27b.backup` verified) |
| `kildall nuke` dry-run | 13,864 entries, 0 outside, 0 refused |

Evidence: `/Volumes/ES2TB/Kildall/code/.session/kildall27b-0-20261122/gates-3/`.

## Known gap (next slice)

Live smoke (`kildall ask "Reply with exactly one word: READY"`): both servers came up on 8423/8424
in 47 s, then the turn stopped with `kildall: Expected the pinned Gemma 4 native chat template`.
`tool_runtime.py` and `tool_grammar.py` only build Gemma 4 native tool calls. A Qwen3.8 tool-call
adapter is needed before any live gate. Evidence: `.../kildall27b-0-20261122/smoke/`.

## Shared with main Kildall on purpose

- Cloud keys: the same Keychain service `kildall`. `kildall keys import` here changes main's keys too.
- Boot daemon `local.kildall.wiredlimit` (20480 MB): one per Mac.
- Git hooks: this worktree uses main's `code/.git` hooks; `secret_scanner.py --install` refuses here.
- Runtime b10809 and Harrier: read from `code/.tools` and `code/models`. `setup_kildall.py` refuses here.
- Not yet split: the frozen recall test (`test_recall.py`) uses ports 8123/8124, so it refuses to run here.
