# Kildall code_1.24 — test version for smaller hardware

Runs Kildall on a 24 GB Mac with only models already on the machine. Cloud is off.

Run: `.venv/bin/kildall ask "your request"`. Close stdin in scripts with `</dev/null`, or Kildall waits for input.

**Fit rule** (`Orbiplan.md` v59): a model is used only if it writes at least 2 tok/s at all times on this Mac. Worst case: the longest context Kildall allows, a 600 s soak, measured. Qwen3.8-Flash-Next (1.1–1.2 tok/s from ES2TB) failed it and was removed.

| Job | Runs on | Real job |
|---|---|---|
| Router, chat, reasoning, coding, debugging, research, translation | gemma-4-26B-A4B (Lane A) | code analysis 19 s, debug 11 s, proof 20 s, translation 5 s |
| OCR, questions about a document image | macOS Vision, then Lane A | 7-9 s |
| Pointing at things in a picture | Nemotron-3.5-Bolt-E4B | 29-64 s |
| Image | SwarmUI (MOSS-Image) | 136 s |
| Video | SwarmUI: first frame with MOSS-Image, then Wan2.2 | 414 s for a 1 s clip (image 2.4 min, then video 3.8 min) |
| Speech in, speech out | whisper-cli, Kokoro | 26 s, 33-62 s |

These picks come from 31 fixed jobs on up to 9 models (`.session/lane-bench-20261106/`). Gemma had the best score and the best time on the hard jobs, so Lane A does the text jobs itself and no model swap is needed.

Fit rule, measured 2026-11-21 (`.session/fit-20261121/`):

| Model | Worst case | Worst write | Result |
|---|---|---|---|
| Gemma, batch 32 | both slots read ~32,380-token prompts at once, 995 s | 2.48 tok/s (19.0 alone) | pass |
| Gemma, batch 64 / 128 | same | 1.78 / 1.08 tok/s | fail |
| Bolt E4B | 7,808-token prompts, 621 s | 20.26 tok/s | pass |

Why batch 32: while one slot reads a prompt, the other slot writes about one token per read batch. The cost: prompt reading drops from ~170 to ~101 tok/s when both slots read. Peak 12.07 GB, 0 warning, 0 critical, no GPU out-of-memory.

Final gates 2026-11-21 (batch 32, wired limit 20480): `test_cli` 18/18, live routing 20/20, the 8 no-model tests pass. Gates at 2 × 32K, 2026-11-06: frozen recall 20/20 on one slot and 20/20 on the work slot; abstention 20/20; callable JSON 20/20; tools 17/20 first pass, 20/20 after retry. Live routing is scored by lane and category only, because code_1.24 runs every lane locally.

Lane A uses ports 8223 and 8224, so it does not block the main `code` folder. It stops after 5 idle minutes (`idle_stop_seconds`), and the next job loads it again in about 45 s. It has 2 slots of 32768 tokens each (router 0, work 1) and uses about 13.5 GB. Only Bolt, image, video and speech jobs stop Lane A; it reloads in the background after them.

Files named in a request are read up front, up to about half the context. A 60 KB file job took 138 s. Long jobs get replies up to 4096 tokens, 7 tool rounds and one last answer turn. Bolt jobs have no tools and get a short system prompt with no tool talk.

SwarmUI lives on ES2TB (`/Volumes/ES2TB/SwarmUI`). After a media job it stays up, so the next media job skips the ComfyUI start (18-76 s). Idle, SwarmUI and ComfyUI hold about 0.8 GB, mostly in swap. Its `ShutdownServer` API stops both.

Known limits:
- `edit` and `write` work only inside the folder where you start Kildall (`permissions.write_root`). They are refused in `/`, your home folder, volume roots and the Kildall vault, except this folder. `install` and `kildall nuke` work only on this folder.
- Edits need a yes typed in a real terminal. With no terminal, the edit is refused and the file does not change.
- Gemma failed the cron coding job and scored 16 of 18 on the hard jobs. Check its code.
- Pointing coordinates are rough: 54 px off for a circle centre, and a box that only partly overlaps the real one (2026-11-21). Check them.
- Qwen3.6-35B-A3B ran out of Metal memory beside Harrier, so it is not used.
- A video job still swaps: the video stage alone (Wan2.2 + text encoder, about 16 GB) added 3.5–3.7 GB of swap (2026-11-21). Making the first frame as its own job cut this from 8.4 GB, but adds about 90 s. Image jobs add no swap.
- Speech recognition is English only (only `ggml-base.en.bin` is on disk). whisper-cli gets the prompt "Kildall", so it spells the name right.
- No rerank or 3D model on disk.

Tests: run each `test_local_lanes.py`, `test_local_media.py`, `test_routing.py`, `test_cloud.py`, `test_router_warmth.py`, `test_permissions.py`, `test_phase44.py`, `test_slot_isolation.py` and `test_cli.py` with `.venv/bin/python`. `test_routing.py --live` takes more than 9 minutes.
