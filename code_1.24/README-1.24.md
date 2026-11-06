# Kildall code_1.24 — test version for smaller hardware

Runs Kildall on a 24 GB Mac with only models already on the machine. Cloud is off.

Run: `.venv/bin/kildall ask "your request"`. Close stdin in scripts with `</dev/null`, or Kildall waits for input.

| Job | Runs on | Real job, 2026-11-06 |
|---|---|---|
| Router, chat, reasoning, coding, debugging, research, translation | gemma-4-26B-A4B (Lane A) | code analysis 19 s, debug 11 s, proof 20 s, translation 5 s |
| OCR, questions about a document image | macOS Vision, then Lane A | 7-9 s |
| Pointing at things in a picture | Nemotron-3.5-Bolt-E4B | 29-64 s |
| Image | SwarmUI (MOSS-Image) | 136 s |
| Video | SwarmUI (Wan2.2) | 314 s for a 1 s clip |
| Speech in, speech out | whisper-cli, Kokoro | 26 s, 33-62 s |

These picks come from 31 fixed jobs on up to 9 models. Gemma had the best score and the best time on the hard jobs, so Lane A does the text jobs itself and no model swap is needed. Bench files are in `.session/lane-bench-20261106/`.

Qwen3.8-Flash-Next stays configured but is not routed. It took 1111-1201 s on the code analysis job that Gemma does in 19 s. On the two hard code jobs it matched Gemma: JSON parser pass (1698 s against 49 s), cron fail (1028 s against 26 s).

Gates at 2 × 32K, 2026-11-06: frozen recall 20/20 on one slot and 20/20 on the work slot; abstention 20/20; callable JSON 20/20; tools 17/20 first pass, 20/20 after retry; CLI 18/18. Routing lane and category 19/20; the one miss (r15) was a crash on a vision job with no image, now fixed. Soak 767 s at about 32,500 tokens per prompt: 140 normal, 13 warning, 0 critical, no GPU out-of-memory, peak 12.2 GB.

Lane A uses ports 8223 and 8224, so it does not block the main `code` folder. It stops after 5 idle minutes (`idle_stop_seconds`), and the next job loads it again in about 45 s. It has 2 slots of 32768 tokens each and uses about 13.5 GB. Only Bolt, image, video and speech jobs stop Lane A; it reloads in the background after them.

Files named in a request are read up front, up to about half the context. A 60 KB file job took 138 s. Long jobs get replies up to 4096 tokens, 7 tool rounds and one last answer turn. Bolt jobs have no tools.

Known limits:
- `edit` and `write` work only inside the folder where you start Kildall (`permissions.write_root`). They are refused in `/`, your home folder, volume roots and the Kildall vault, except this folder. `install` and `kildall nuke` work only on this folder.
- Edits need a yes typed in a real terminal. With no terminal, the edit is refused and the file does not change.
- Gemma failed the cron coding job and scored 16 of 18 on the hard jobs. Check its code.
- Bolt gave no pixel coordinates in testing. Qwen3.6-35B-A3B ran out of Metal memory beside Harrier, so it is not used.
- No rerank or 3D model on disk. Speech recognition is English only, and it misheard "Kildall" as "Killdoll".

Tests: run each `test_local_lanes.py`, `test_local_media.py`, `test_routing.py`, `test_cloud.py`, `test_router_warmth.py`, `test_cli.py` with `.venv/bin/python`. `test_permissions.py` and `test_phase44.py` also pass.
