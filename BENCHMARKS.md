# Kildall measurements

Current checkout and sole mutation root: `~/Kildall/code`. Current backup
registration command: `~/Kildall/code/.venv/bin/kildall --schedule-backups`.
Historical commands, errors and raw evidence below retain their original path
spellings; the rename validation records the authorized path-only comparison.

Phase 1 is in progress. No candidate has passed all four gates yet.

## Reference and gates

- Existing baseline: **qwen3:8b, 19.48 tok/s**, prompt evaluation 100 tok/s,
  load 4.1 s, measured 2026-09-06. It has not been re-measured.
- Gate (a): generation throughput **>15 tok/s**; also compare against 19.48 tok/s.
- Gate (b): routing **>=18/20**. Gate (c): callable tool JSON **20/20**.
- Gate (d): record peak RAM and system memory pressure during **ten minutes** of load.
- Host: Mac mini M4, 10 CPU / 10 GPU cores, 24 GiB RAM, wired limit 20480 MB.
  Free disk before download: 253.63 GB. Before the first run, system free-memory
  percentage was 66% and pre-existing swap usage was 2975.94 MiB.

## Candidate 1: Qwen3.8-Flash-Next

Model: `unsloth/Qwen3.8-Flash-Next-GGUF`, revision
`38bb39ee97821de2c9009abb7e93950eec396e66`, `UD-IQ4_XS`.
Three GGUF shards total **93,682,584,224 bytes**; each size and SHA-256 was
verified against Hugging Face metadata. Download took approximately 56 minutes.
Weights are stored locally under `models/qwen3.8-flash-next/UD-IQ4_XS/`, excluded from Git.

The upstream license is **Qwen Community License 1.0**, correcting the planning
file's Apache-2.0 label. Sources: [official model](https://huggingface.co/Qwen/Qwen3.8-Flash-Next),
[license](https://huggingface.co/Qwen/Qwen3.8-Flash-Next/blob/de4b8e4d43b917e7706784d8bb445c9af86a3540/LICENSE),
[quantization](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF/tree/38bb39ee97821de2c9009abb7e93950eec396e66/UD-IQ4_XS).

Runtime: upstream llama.cpp **b10809**, commit
`5266f24da75dc449bd56cbed7addb9c8e4a6a73e`, the binary referenced by stable v0.4.0.
The installed Homebrew b10360 predates this model's architecture support.
The [arm64 runtime archive](https://github.com/ggml-org/llama.cpp/releases/download/b10809/llama-b10809-bin-macos-arm64.tar.gz)
was size- and SHA-256-verified: 11,123,196 bytes,
`7d692df9e1e386e62f1c12b843903218041e6cd74c9415aa39a7ed3176f9eaa2`.
Runtime lives under `.tools/llama-b10809/llama-b10809/`, excluded from Git.

Prompt: "Explain how a local command-line assistant can keep useful project memory
while limiting retrieved context. Give a clear practical answer."

Common flags:

```sh
-lm mmap --lazy-mode on --cpu-moe --no-repack --no-op-offload \
-c 4096 -t 8 -ctk q8_0 -ctv q8_0 -fa on --offline --no-warmup \
--perf -n 128 --seed 42 --temp 0 --simple-io --single-turn
```

| Run | GPU layers | Batch / ubatch | Result | Elapsed | Maximum RSS |
|---|---:|---:|---|---:|---:|
| 1 | all | 128 / 128 | Metal OOM before valid generation | 77.62 s | 7,937,196,032 bytes |
| 2 | 8 | 32 / 32 | **0.21 tok/s — FAIL gate (a)** | 703.24 s | 14,425,473,024 bytes |

Run 1 exact errors:

```text
Insufficient Memory (00000008:kIOGPUCommandBufferCallbackErrorOutOfMemory)
llama_decode: failed to decode, ret = -3
Compute error.
```

**Run 1 exited 0 despite the compute errors. It is a failed run, with no valid
tok/s measurement.** A successful process exit alone is insufficient for this runtime.
The 78-second failed run does not satisfy gate (d).
Raw stdout, stderr and exit statuses are retained in `.session/flash-next-throughput.*`
and `.session/flash-next-retry.*` locally.

The first runtime archive transfer also failed with
`http.client.IncompleteRead: IncompleteRead(8189970 bytes read, 2933226 more expected)`.
A curl retry recovered it and passed the full size/hash check before extraction.

Run 2 completed 128 generated tokens in 600,408.85 ms; llama.cpp reports **0.21 tok/s**.
Prompt evaluation: 76 tokens in 60,105.95 ms, **1.26 tok/s**. No compute error occurred.
This fails both the >15 tok/s gate and the 19.48 tok/s reference. Routing and tool gates
were skipped as instructed after gate (a) failed. Although the run lasted 703.24 seconds,
it was not a continuously sampled ten-minute memory-pressure test; gate (d) is unmeasured.
No Lane A winner or recall score is claimed.

## Candidate 2: Qwen3.8-27B + CMoE

**Unsupported as specified; not downloaded or benchmarked.** No verified converted
Qwen3.8-27B checkpoint or compatible Metal runtime was found. This is an availability
blocker, not a measured 0 tok/s result.

At official [CMoE revision 42dfc947](https://github.com/JarvisPei/CMoE/tree/42dfc94777a0de3620a67bdb5000d7fec56e5b6a):

- `run_cmoe.py` loads Llama/Llava classes, requires CUDA and assumes `model.model.layers`.
- `CMoE_utils.py` calls self-attention in every layer. Qwen3.8-27B's
  [configuration](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/config.json)
  uses `Qwen3_5ForConditionalGeneration` with hybrid linear/full attention.
- `CMoE_model.py` implements a custom two-projection router. Upstream b10809's
  Qwen35 MoE graph cannot reproduce it simply by renaming or exporting tensors.
- The repository provides no GGUF exporter or Metal implementation. Its documented
  zero-sample route also conflicts with an `inps[0]` access and unconditional
  fine-tuning call in the published runner; these are source findings, not executed errors.

A dense, unconverted Qwen or a differently trained MoE would not be this candidate.


## Candidate 3: Gemma 4 26B-A4B

**Downloaded and hash-verified; first speed/quality run completed.** Ordered fallback after candidate 1's
measured speed failure and candidate 2's implementation blocker.

- Official model: [google/gemma-4-26B-A4B-it](https://huggingface.co/google/gemma-4-26B-A4B-it),
  revision `4d7ae4984b7db7de8f8457170b3f1a419ee76d52`; Apache-2.0 in the current official card.
- Quantization: [unsloth/gemma-4-26B-A4B-it-GGUF](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF/tree/c099eb48e663fd284577b04978a94ffccb261841),
  revision `c099eb48e663fd284577b04978a94ffccb261841`.
- File: `gemma-4-26B-A4B-it-UD-IQ4_XS.gguf`, **13,597,177,568 bytes**.
  Expected SHA-256: `babd1e389d386352f71600765d37390f7dc993fbfad6725caccf996ffe34aecf`.
- Same b10809 runtime; intended flags: `-lm mmap -ngl 99 -fa on -ctk q8_0 -ctv q8_0
  -np 1 -c 4096 -t 8 --jinja --reasoning off --offline --perf`.
  Context is capped at 4,096 for these gates; larger contexts are not certified by this run.
- Quantization scope: this is the publisher’s GGUF importance quantization for the requested
  llama.cpp runtime. The plan’s MLX-only DWQ procedure does not apply to a GGUF file; no DWQ
  result or equivalent quality is claimed. Flash attention and Q8 KV must be confirmed in the load log.

### Frozen quality and RAM protocol

`bench_cases.json` contains 20 routing requests and 20 synthetic tool requests. Its SHA-256 is
`fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`.
The referenced prompt set was absent from Task 2, so these cases were created and frozen before
seeing any candidate's quality output. They sample the plan's skill/lane policy; they do not
certify every skill in the research taxonomy. No synthetic function is executed.

`benchmark.py` evaluates the model plus llama.cpp's native tool parser and strict function
schemas through its local HTTP API. Valid tool JSON and exact intended arguments are reported
separately. Routing requires exact skill/lane JSON; requests use temperature 0 and seed 42.
The RAM gate maintains generation load for at least 600 seconds and samples process RSS,
system pressure and free-memory percentage every five seconds. Pass criterion set before the
run: pressure remains normal and system free-memory percentage stays at least 10%.
The sampled RSS maximum is labeled as such; `/usr/bin/time -l` additionally records the
server's process high-water RSS after shutdown.

```sh
.venv/bin/python benchmark.py speed --output .session/gemma-speed.json
.venv/bin/python benchmark.py quality --output .session/gemma-quality.json
.venv/bin/python benchmark.py soak --pid SERVER_PID --output .session/gemma-soak.json
```

2026-09-07 recovery: the initial Xet transfer exited 1 after exhausting retries:

```text
RuntimeError: Task error: File reconstruction error: CAS Client Error: Format error: I/O error: error decoding response body
```

No final Gemma weight file or verified hash was produced. Retrying the same pinned artifact
with resumable HTTP; no new candidate or quantization has been selected.


### First Gemma run (2026-09-07)

HTTP recovery completed with exit 0 in **863.10 seconds**, all 13,597,177,568 bytes and
SHA-256 verified before loading. Throughput: **25.2986 tok/s**, beating the 19.48 reference.
Routing's required flat JSON shape passed **1/20**. Post-hoc inspection found all **20/20
skill/lane choices correct**, but 19 replies used nested objects or Markdown fences. This
inspection does not replace the failed format gate. Tool calls: **20/20 schema-valid JSON**,
**19/20 exact arguments**; `t07` added punctuation/escaping to the requested regex.
Process high-water RSS: **4,276,174,848 bytes**. RAM soak skipped after the quality gate failed.

The original outputs are preserved under `.session/*-unconstrained.*`. Retesting the same frozen
cases with a standard strict JSON response schema for routing; enums allow every listed skill
and lane and do not encode expected answers. Tool schemas, prompts, seed and temperature stay
unchanged. This measures the usable constrained-output integration, not unconstrained formatting.


### Constrained routing retest (2026-09-07)

Same frozen cases and model, routing schema enforced through the server API:
**26.1991 tok/s**, **20/20 routing**, **20/20 schema-valid tool JSON**, **19/20 exact arguments**.
The original regex mismatch remains; no expected answer or prompt was edited to hide it.
The completed ten-minute memory-pressure run failed, as detailed below. The model-load log confirms 31/31
layers on GPU, flash attention enabled, a 12,952.19 MiB mapped model buffer and 175.31 MiB
of Q8 KV cache. These allocation figures must not be confused with CPU RSS.

Full-GPU gate (d) **FAILED** after **606.30 seconds**: minimum system free memory **13%**,
kernel warning pressure (level 2). Sampled peak RSS **9,851,535,360 bytes**; true process
high-water RSS **12,086,706,176 bytes**. This is a real ten-minute failure, despite passing
speed and quality. Preserved as `.session/*-full-gpu.*`. Retrying the same model with the
first four expert layers on CPU (`--n-cpu-moe 4 --no-repack --no-op-offload`) to reduce
GPU residency. No gate threshold or fixture is relaxed.


### CPU-expert retry (2026-09-07)

The same Gemma weights with `--n-cpu-moe 4 --no-repack --no-op-offload` reached
**23.2194 tok/s**, **20/20 routing**, **20/20 schema-valid tool JSON**, and **19/20 exact
arguments**. Warning memory pressure persisted; the GPU mapped model buffer remained
12,952.19 MiB. The operator stopped this retry after **363.82 seconds**. This is **not** a
second ten-minute measurement. The resulting `RemoteDisconnected('Remote end closed
connection without response')` and shutdown signal were operator-induced.
Sampled peak RSS **2,833,924,096 bytes**, process high-water RSS **9,793,257,472 bytes**,
minimum system free memory **13%**. Global GPU in-use memory peaked at **14,637,809,664
bytes**, including other applications. Evidence: `.session/*-cpu4.*`.
Gemma has not passed gate (d); its full-GPU 606.30-second failure remains recorded above.

## Candidate 4: Granite 4.1 8B — gates in progress

The final candidate uses IBM's official Apache-2.0
[GGUF publication](https://huggingface.co/ibm-granite/granite-4.1-8b-GGUF/tree/865b82c2e7970d82e3731278c88c57ae7138359c).
Pinned revision: `865b82c2e7970d82e3731278c88c57ae7138359c`.
File: `granite-4.1-8b-Q4_K_M.gguf`, **5,347,914,400 bytes** (the actual artifact is larger
than the plan's approximately 4.3 GB estimate).
Expected SHA-256: `ed902ac9eb6adce5a90c6a08c8ea201b50e23fdc5976d1cd0362006afac5309e`.
The transfer must pass full size/hash verification before loading. All GPU layers, mmap,
Q8 KV, flash attention, 4,096 context, batch/ubatch 128, eight threads, and the same frozen
quality fixtures will be used. No throughput or gate result is inferred from qwen3:8b.


### Granite Q4_K_M (2026-09-07)

Download verified: **258.27 seconds**, exact size and SHA-256 matched. b10809 confirms
**8.79 billion parameters**, 41/41 layers on GPU, flash attention enabled, 5,096.77 MiB
mapped GPU model buffer and 340 MiB Q8 KV cache.
Throughput: **17.4853 tok/s**. This passes gate (a), but **does not beat the 19.48 tok/s
baseline required in the task context**. Routing: **19/20**. Tool calls: **20/20 schema-valid
JSON**, **14/20 exact intended arguments**. The completed RAM gate passed after
**605.39 seconds**: all 120 samples had normal pressure, minimum free memory **63%**,
sampled peak RSS **7,059,750,912 bytes**, process high-water RSS **7,060,520,960 bytes**.
Global GPU in-use memory peaked at **6,503,481,344 bytes**, including other applications.
All four explicit gates pass, but the additional baseline requirement fails. Lane A remains
unchosen; passing 15 tok/s does not imply beating 19.48 tok/s.

Testing IBM's smaller **Q3_K_M variant of the same candidate** next, with all four gates
measured independently. Its pinned revision is unchanged; size **4,347,048,608 bytes**,
SHA-256 `b099e58ec0a71a368fa68f08f1ea66c0f0e96fe13d621482f8456bbf4c213ad9`.
It will load only after the Q4 server has stopped and the download's full hash is verified.

The RAM evaluator now also rejects runs with zero completed generation requests.
Deterministic checks cover normal pressure, recovered warning pressure, sampling errors,
and no completed load. This does not rescore previous real runs, which all completed many
requests; synthetic checks are not model scores.


Q3_K_M download completed in **233.07 seconds**, exact size and full SHA-256 verified.
The first Q3 startup attempt failed before model loading with `OSError: [Errno 48] Address
already in use`. There was no live listener after the Q4 shutdown; enabling SO_REUSEADDR
in the port preflight resolved the TIME_WAIT collision. The retry loaded successfully.
Q3 throughput measured **15.6914 tok/s**, slower than Q4 and below the baseline.
The operator stopped the quality subprocess after this finding; incomplete quality is
**unscored**, RAM skipped. Exact wrapper error: `RuntimeError('quality exited -15 without a
fresh result')`. This was an operator stop, not a spontaneous model failure. Process
high-water RSS before stopping: **4,863,442,944 bytes**.


### Gemma whole-layer placement retest (2026-09-07)

Reusing the existing IQ4_XS weights, `-ngl 27 --no-repack --no-op-offload` puts three
of 30 transformer layers plus the output layer on CPU (27/31 layers offloaded). This
corrects the initial shorthand description of "four complete layers": only three are
transformer blocks. Throughput **23.3135 tok/s** beats the baseline. Early pressure is
normal with **31% free memory**, but the mapped GPU buffer still reports 12,952.19 MiB;
no reduced physical residency or causal improvement is inferred from the flag alone.
Quality and a full ten-minute memory run are pending. Evidence uses `.session/gemma-layers4-*`.


Whole-layer retest completed: **20/20 routing**, **20/20 valid tool JSON**, **19/20 exact
arguments**. RAM **failed** after **604.72 seconds**: 94 normal-pressure samples and
26 warning-pressure samples, minimum free memory **19%**. Sampled peak RSS
**13,520,551,936 bytes**, process high-water RSS **13,520,896,000 bytes**. Global GPU
in-use peak **14,355,349,504 bytes** includes other applications. The early normal-pressure
snapshot did not predict the full-duration result; no winner was selected.

### Smaller Gemma quantization (2026-09-08)

Next test uses the same candidate, publisher and pinned revision with **UD-IQ3_S**:
`gemma-4-26B-A4B-it-UD-IQ3_S.gguf`, **11,289,671,136 bytes**,
SHA-256 `878be93f9c238ea853b3fd1eb602637ce3cf1cddea56dc345d9a7bf2d6093e29`.
The 2.31 GB reduction addresses model footprint directly; neither quality nor speed is
assumed to carry over. Download verification and all four measurements are pending.
This run returns all layers to GPU with mmap, Q8 KV, flash attention and 4,096 context.


IQ3_S transfer completed using a verified 2,844,942,336-byte prefix plus four HTTP ranges;
range transfer/assembly took **322.62 seconds**. Each range and the complete **11,289,671,136
bytes** matched; the assembled SHA-256 matched before loading. A subsequent metadata
round-trip assertion failed because tuples become JSON lists. The artifact was independently
full-hashed again; the assertion and publish-after-verification ordering were fixed. No bad
weight file was loaded, and temporary parts were removed only after verification.

IQ3_S throughput **29.4857 tok/s**; routing **20/20**, valid tool JSON **20/20**, exact intended
arguments **18/20**. The smaller quantization's quality was measured independently with the
unchanged frozen fixture. Its ten-minute RAM run is in progress; early normal pressure does
not replace the full-duration gate.


IQ3_S's first RAM gate **failed** after **602.41 seconds**: 89 normal and 31 warning
samples; warning began at **449.45 seconds**, minimum free memory **20%**, process
high-water/sample-peak RSS **13,589,856,256 bytes**. Global GPU in-use peak was
**12,111,396,864 bytes**. No request failed, but the pressure requirement did.

### Prompt-cache root cause and retest (2026-09-08)

The load log revealed an **8,192 MiB server prompt-cache limit**. By the end of this run
it held **126 prompts / 3,588.711 MiB**, even though HTTP requests used `cache_prompt=false`.
That request setting controls prompt reuse and does not disable the server cache. This
explains an increasing host allocation while the GPU model allocation stayed steady.
The recorded failures remain valid for those configurations; they do not prove the weights
alone exceed RAM. Retesting IQ3_S with **`--cache-ram 0`**, all other model/fixture settings
unchanged. No further weight download or gate relaxation.

The runner also now sends shutdown SIGINT to the actual server child once. Sending it to
both `/usr/bin/time` and its child caused the wrapper to forward a second interrupt and
force termination, including a Metal `rsets` cleanup assertion. That was harness-induced
shutdown behavior after the measurements, not a spontaneous inference failure.


## Lane A selected — 2026-09-08

**Gemma 4 26B-A4B, Unsloth UD-IQ3_S, with the server prompt cache disabled** qualifies.

| Gate | Measured result |
| --- | --- |
| Throughput | **29.3336 tok/s**, above15 and the19.48 baseline |
| Routing | **20/20** |
| Callable tool JSON | **20/20**; exact intended arguments **18/20** |
| RAM | **601.43 seconds**, all **120 samples normal**, minimum free **34%** |

Sampled peak RSS **11,943,804,928 bytes**; process high-water RSS **12,229,640,192 bytes**.
Global GPU in-use peak **12,292,702,208 bytes**, including other applications. No request
errors; server shut down normally with exit0. Evidence: `.session/gemma-iq3-nocache-*`.

The winning flags are `-lm mmap -ngl99 --cache-ram0 -fa on -ctk q8_0 -ctv q8_0 -np1
-c4096 -t8 -b128 -ub128 --jinja --reasoning off --offline --perf` (each option/value is
passed as a separate argument). This certifies4,096 context, not32K. The default server
prompt cache must remain disabled in Orbi. Neither the original Qwen baseline nor the
failed candidates/configurations above were relabeled or erased.

## Phase 1 integration validation — 2026-09-09

Real Harrier embeddings plus the selected Lane A scored **19/20 recall pairs**
(required:17). All20 queries used semantic retrieval alongside BM25. Worst measured
retrieval wall time was **124.349 ms**; maximum returned context was **12 items /
1,798 characters**. Every query stayed within12 items/4,000 rendered characters/300ms,
and no other-project fact leaked. These are model measurements, separate from the
synthetic-vector unit checks of cap enforcement, stalled IO and scope filtering.

The20 fictional facts/questions, accepted aliases and strict normalized-equality
scoring were frozen before any model request. Fixture SHA-256:
`888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`.
**Failure retained:** recall-18 asked who owns the go-live checklist. The relevant
release-coordinator fact was not retrieved; the model answered `UNKNOWN` instead of
`Imani Tran`. Neither the question nor its aliases were changed after the run.
Reproduce with `test_recall.py`; raw results remain locally in `.session/recall-results.json`.

Delete-then-restore of the isolated test database preserved all30 records (20 facts,
10 foreign-project distractors) and their exact1,024-dimensional vectors; the markdown
mirror was verified. Production snapshots and mirrors live outside code at `../backups`.
The03:00 launchd job was registered and manually triggered: **last exit code0**, snapshot
integrity verified. Registration covers the current login; run `orbi --schedule-backups`
after logging in again. Retention is14 days within this database's snapshot namespace.

`test_cli.py` passed all18 checks (14 integration checks and four control groups), including streaming,
continuation, real global remember/recall across projects, project-session isolation,
pipes, PTY input with clean piped output, oversized-context rejection, Ctrl-C exit130,
SIGKILL recovery, all seven persisted orb states, stall detection and corrupt-artifact
rejection. Local HTTP ignores environment proxies. Test data stayed isolated from the
production database. The control checks cover shared turn/exclusive restore admission
across processes, continuation ordering, bound-port ownership before HTTP, and missing
persistence rows. A direct CLI restore call also fails before mutation while a turn holds
admission. Evidence: `.session/cli-results.json`.

Final `./check.sh` exited **0** with all five lines: Python **3.12.13**, MLX
**`Device(gpu, 0)`**, **`iogpu.wired_limit_mb: 0`**, **127.31 GB free** on the data volume,
and the unchanged recorded19.48tok/s baseline. The current wired-limit reading differs
from the earlier20,480 setting; no sysctl write or sudo was performed during this check.
All2,158 protected planning/research snapshot entries matched their recorded hashes.

## Lane A re-test preflight — 2026-09-09

**The requested DWQ comparison has not run.** The user confirmed the manual sysctl
change, and a read-only check returned `iogpu.wired_limit_mb: 20480` before any model
measurement. No model was downloaded, deleted, loaded or benchmarked during this preflight.
Phase2 has not started, and the existing Gemma weights/config remain available.

The exact frozen `bench_cases.json` SHA-256 is
`fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`.
Prompts, schemas, expected answers and scoring are unchanged. The new ranking is
**exact argument accuracy first, throughput second**, with greater than15tok/s sufficient;
beating19.48tok/s is no longer an acceptance requirement. All model results below are
unmeasured under the requested DWQ/32K protocol, not zero scores.

| candidate | quant | tok/s | routing | callable JSON | exact args | peak RAM |
| --- | --- | --- | --- | --- | --- | --- |
| Granite 4.1 8B | DWQ4-bit requested; no matching published checkpoint found | N/A | N/A | N/A | N/A | N/A |
| Qwen3.8-27B + CMoE | DWQ4-bit requested; CMoE unsupported here | N/A | N/A | N/A | N/A | N/A |
| Gemma 4 26B-A4B | Published MLX4-bit DWQ; not loaded | N/A | N/A | N/A | N/A | N/A |

### Protocol conflict requiring a decision

The protected plan itself labels DWQ **MLX only**, then prescribes llama.cpp load flags.
The discovered Gemma DWQ artifact is
[`catalystsec/gemma-4-26B-A4B-it-4bit-DWQ`](https://huggingface.co/catalystsec/gemma-4-26B-A4B-it-4bit-DWQ/tree/c50241db43deef70c71a4bd0e1f32ff9229aeec0),
revision `c50241db43deef70c71a4bd0e1f32ff9229aeec0`: three MLX Safetensors shards,
affine4-bit/group64 config, and no GGUF artifact. Its card names DWQ but does not publish
a calibration recipe or training log, so the name alone is not independent verification
of its build history. Searches for Granite4.1-8B found standard MLX and GGUF quants,
but no matching DWQ checkpoint. Search metadata/cards were saved under
`.session/retest-20260909/`; only metadata was fetched.

[Apple's DWQ documentation](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LEARNED_QUANTS.md)
describes learned scales/biases with a teacher and MLX output. Installed mlx-lm0.31.3's
DWQ implementation saves that MLX format; its converter has no GGUF export option.
The installed llama.cppb10809 expects GGUF. No supported route was found that preserves
these learned weights in the requested llama.cpp execution path. Re-quantizing them to
a regular GGUF cannot simply be labeled the same DWQ build, and DWQ does not guarantee
6-bit-equivalent quality on every model. No incompatible flags or substitute quantization
were silently used. A user decision is pending: MLX DWQ with corresponding MLX settings,
or llama.cpp with explicitly documented GGUF quantizations.

### Qwen + CMoE: skipped as unsupported, not a throughput failure

Rechecked official CMoE HEAD `42dfc94777a0de3620a67bdb5000d7fec56e5b6a`.
[`run_cmoe.py`](https://github.com/JarvisPei/CMoE/blob/42dfc94777a0de3620a67bdb5000d7fec56e5b6a/run_cmoe.py#L17)
hardcodes `torch.device('cuda:0')`, calls `.cuda()`, and dispatches only Llama/Llava.
This Mac is Darwin arm64 with no NVIDIA CUDA device; the project environment also has
no Torch installed. Installing Torch alone would not supply CUDA or Qwen support.

The [official Qwen config](https://huggingface.co/Qwen/Qwen3.8-27B/blob/1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0/config.json)
uses `Qwen3_5ForConditionalGeneration` with48 linear-attention and16 full-attention layers.
CMoE assumes `layer.self_attn` throughout. Its [two-projection router](https://github.com/JarvisPei/CMoE/blob/42dfc94777a0de3620a67bdb5000d7fec56e5b6a/CMoE_model.py#L31)
and ungated shared experts also differ from the installed
[Qwen35MoE graph](https://github.com/ggml-org/llama.cpp/blob/5266f24da75dc449bd56cbed7addb9c8e4a6a73e/src/models/qwen35moe.cpp#L493).
The official source tree has no Qwen/Metal/MPS/GGUF export implementation; no matching
Qwen3.8-27B-CMoE checkpoint was found. An unrelated Llama8B CMoE GGUF exists, but provides
no verified route for this candidate. llama.cpp's `-cmoe` means CPU placement of existing
MoE weights; it does not perform this conversion. This is a source/runtime compatibility
finding, not a fabricated execution error: conversion/inference were not attempted,
and the unconverted dense model was not substituted.

### Health and backup fixes completed

`check.sh` now exits1 and prints the exact manual sysctl command when the wired limit is0.
It also checks the loaded launchd job against the expected program, arguments, config,
working directory and03:00 calendar schedule; missing/mismatched registration exits1.
The first implementation incorrectly expected unquoted launchctl calendar keys and
reported `WARNING: Nightly backup registration is missing or mismatched.` despite an
existing job. Inspection showed quoted `"Hour"`/`"Minute"` keys; matching was corrected
and the real check now exits0, with the registered03:00 job verified.

`test_check.py` passed reset-to-zero, missing-registration, wrong-hour and wrong-program
checks, including optimized Python. These tests mocked read-only command results;
they did not change sysctl or launchd. The real check reports Python3.12.13,
`Device(gpu, 0)`, wired limit20480,127.11GB free, and the unchanged recorded baseline.
README documents the exact post-login command:
`/Users/minhduc/Orbi/code/.venv/bin/orbi --schedule-backups`.
The current-login scheduling approach is retained, as the user explicitly allowed
documented re-registration; no file was written outside code, including CLAUDE.md.

### MLX comparison authorized — 2026-09-10

The user approved replacing the llama.cpp-specific flags with MLX settings while
retaining32K context,8-bit KV and ten-minute monitoring. Wired limit20480 was verified
again. CMoE remains skipped for the recorded compatibility reasons.

Granite's DWQ recipe is fixed before any new benchmark answer: official BF16 teacher
`ibm-granite/granite-4.1-8b` revision `1504002f650e656a0a3789d99574df12e3e94ed0`,
MLX affine4-bit/group64 student,128 calibration examples plus32 validation examples,
257 tokens maximum, batch1, seed123, one DWQ pass, learning rate1e-6. Calibration comes
from eight evenly spaced20-row pages of `allenai/tulu-3-sft-mixture`, shuffled once
and saved before model use. No `bench_cases.json` input or answer is used for calibration.
Teacher targets are computed in a separate process to avoid keeping the BF16 teacher
resident alongside the student. Artifact sizes and complete hashes are verified before use.
This is a small local DWQ build, not a claim of a publisher-certified optimized quant.

Installed mlx-lm0.31.3's default Gemma cache raises
`NotImplementedError("RotatingKVCache Quantization NYI")` for8-bit KV. The comparison
will use full quantized caches while preserving Gemma's explicit1024-token sliding
attention masks, with a hard prompt-plus-reply limit of32768 and fresh caches per request.
This retains more KV history than a rotating cache. Also, MLX8-bit KV uses quantized
matrix multiplication/softmax attention, **not Flash Attention**; no FA claim carries over
from the llama.cpp runs. These backend differences and actual observed cache/attention
types will be recorded, rather than hidden behind flag names.

### Granite artifact preparation — 2026-09-10

All four official BF16 shards and accompanying metadata passed full pinned hash
verification (`models/granite-4.1-bf16/orbi-artifact.json`). The initial sequential
transfer was operator-interrupted to resume the same partial files with four parallel
transfers; curl exited with `CalledProcessError: died with <Signals.SIGINT: 2>`.
The resumed transfer completed successfully; this was not a model execution failure.
Frozen independent calibration SHA256:
`d063e2be1c39f5aec1e5d4f451b664be4f7c4a1634255df61186f37db377ccb1`.

The first teacher-target attempt failed before inference:
`ValueError: Received 1 parameters not in model: lm_head.weight.`
The official checkpoint declares tied embeddings but includes a duplicate head tensor;
installed MLX Granite has no sanitizer for it. Preparation now verifies exact tensor
and dtype equality with the embedding before removing only that duplicate from the
loader input. Other weights still undergo strict loading; original source files are
unchanged. Tiny duplicate/mismatch checks passed. Original failure log is retained at
`.session/retest-20260909/granite-targets.log`; retry log is `granite-targets-2.log`.

The MLX harness now uses the requested strict >15 tok/s gate; beating19.48 remains a
reported comparison only. All-mode continues through quality and ten-minute monitoring
even after a speed miss. Frozen fixture hash is checked before model loading. MLX uses
its installed default argmax sampler, fresh8-bit caches,256MiB allocator cache,
20GiB allocation limit and18GiB process wired limit for both candidates. These process
limits do not modify sysctl. Synthetic KV, timing, context and tool-parser checks pass.

During the BF16 teacher's initial load, a read-only spot check observed pressure4,
13% free and6,141.69MiB swap used; a later check showed pressure1,16% free and8,011.19MiB
swap used. Targets then progressed normally. These preparation observations are not
candidate inference RAM-gate measurements. Subsequent samples are retained in
`granite-targets-memory.jsonl`.

Inspection also confirmed `stream_generate` temporarily changes the MLX process wired
limit to the device's recommended working set and restores18GiB afterward. The harness
records both values rather than claiming18GiB remains active during generation. Sysctl
remains20480. This installed-library behavior is identical for both candidates.

Teacher generation completed with exit0 and all128 train/32 validation target files
verified. Continuous post-load monitoring recorded pressure1 throughout; transient
load pressure was separately recorded above. DWQ training started with initial held-out
KL loss0.079. This is calibration evidence, not a routing/tool score.

The new MLX harness is committed as `7e6db03`; its runnable synthetic checks and existing
benchmark evaluator checks pass. It keeps all frozen prompts/scoring intact and runs no
real tools. Granite's tokenizer selects the installed native JSON tool-frame parser;
Gemma uses its native function-call parser. Neither backend enforces a JSON grammar,
whereas historical llama.cpp routing runs did, so those historical scores are not a
same-backend quantization-only comparison.

Gemma's three direct shard transfers were operator-interrupted after slow progress,
then resumed from their preserved prefixes using the already-proven Phase1 HTTP-range
method, with18 independent ranges. Range offsets, final shard sizes and complete SHA256
must pass before use. Only the code-local retest transfer script is run; old transfer
scripts that write root CLAUDE.md are not executed. Original interruption evidence is
retained in `gemma-dwq-download.log`; range evidence is in `gemma-range-download.log`.

To avoid idle time during Gemma's transfer, Granite's deterministic accuracy-only run
will use `benchmark_mlx.py quality` after its DWQ build is verified. This run may overlap
network transfer; its timing is not used for the throughput or RAM gate. Dedicated speed
and600-second soak runs wait until downloads finish. All runs use the same frozen
messages, argmax, local weights and8-bit KV settings; no answers will be used to revise
the calibration recipe or prompts. The mode-specific result files retain this separation.

### Granite DWQ build verified

Preparation exited0. Held-out KL loss improved from0.079 to0.071 (printed precision),
and439 quantization scale/bias arrays changed. The final affine4-bit/group64 student is
4,714,642,545 bytes, SHA256
`827f8ef77845348b6dc04dfe6d54c56bf4f84c5b4fd1baec8632badc14a8cdd6`.
Build provenance is `models/granite-4.1-dwq-4bit/orbi-dwq-build.json`; complete output is
`.session/retest-20260909/granite-dwq-build.log`. These demonstrate an executed DWQ pass,
not merely a renamed ordinary4-bit checkpoint. This calibration result does not imply
a particular tool score or6-bit-equivalent quality.

### Granite DWQ accuracy result — measured, failed

The accuracy-only process exited1: **routing0/20, callable JSON20/20, exact arguments14/20**.
All20 routing responses failed strict JSON parsing; 1 began with Markdown fences,
and others answered the task instead of returning a route. The first exact error was
`JSONDecodeError('Expecting value: line 1 column 1 (char 0)')`. A tokenizer-only check
confirmed the complete frozen system policy is present in the rendered prompt; it was
not dropped by the template. No response cleanup or grammar was added after this result.

Wrong exact-argument cases: `t03`, `t04`, `t06`, `t07`, `t12`, `t16` (quoted paths/text,
regex and Unicode). This does not meet the requested improvement over Gemma's18/20.
Raw responses and error strings are retained in
`.session/retest-20260909/granite-dwq-quality-run-quality.json`; aggregate run metadata is
`granite-dwq-quality-run.json`. File SHA256:
`082a3a7eecd0c62dc11003907cf03b406598dd734a51cc9f1d8f94ef7d6af10e`.
Peak process RSS during this accuracy run was5,008,474,112 bytes;
MLX peak allocation was5,057,154,938 bytes. These are not yet a ten-minute
RAM gate. Dedicated speed and soak measurements remain pending transfer completion.

### Gemma DWQ download verified

All18 HTTP ranges, three assembled shards and the complete artifact manifest passed
verification; both assembly and final verification exited0. Published revision:
`c50241db43deef70c71a4bd0e1f32ff9229aeec0`. Weight files total
14,194,825,720 bytes.
Final hashes:

- `model-00001-of-00003.safetensors`: `9d6aec37b137f30823970aca155341480cdb3ef7d2b6e4995f7a04940d4c1985`
- `model-00002-of-00003.safetensors`: `b6a4170d64ee67b6f0e612fb998956ef5792576c4118a374cc9052aadedeca09`
- `model-00003-of-00003.safetensors`: `77e7d7aeaf518512a4f50c5e96a85b234dfee8d6410de88d685baead93e13ab8`

Original IQ3_S Gemma weights remain intact. All downloads and hashing have finished;
dedicated throughput and ten-minute RAM measurements now run without that I/O.

Granite's dedicated speed run exited0: **19.48594417 tok/s**, passing the strict
>15 gate. It used127 post-first-yield tokens over
6.517518 seconds, including final GPU drain.
Raw timing: `.session/retest-20260909/granite-dwq-speed-run.json`.
The dedicated600-second RAM run has started.

### Granite DWQ RAM gate complete

Dedicated soak exited0: 607.468838 seconds total, with120 samples
and the last sample at602.844070 seconds. All pressure readings were1 (normal),
minimum free memory was66%, and the monitor/generation error list
was empty. Peak sampled GPU in-use memory was5,303,894,016 bytes.
True process RSS peak across speed, accuracy and soak was5,008,474,112 bytes
(5.008GB). MLX allocator peaks are retained separately in each result file.
Raw soak: `.session/retest-20260909/granite-dwq-soak-run.json`.

Granite passes speed and RAM, but fails routing and reaches only14/20 exact arguments;
it is not a replacement for the existing Gemma Lane A. Gemma's full DWQ run has started
with the same harness/settings and no simultaneous model run or download.

### Gemma DWQ initial measurements and routing-control correction

Gemma's dedicated speed gate in the full run measured **39.24433842
tok/s**. Unconstrained accuracy was **5/20 routing,20/20 callable JSON,
18/20 exact arguments**. Wrong exact cases:
t07, t12.
The immediate post-load sample showed pressure2 (warning),33% free; subsequent spot
checks showed pressure1. The full600-second soak is still running, so its RAM outcome
is not yet claimed. Original result: `gemma-dwq-all-run.json` and its per-mode files.

**Protocol correction:** the first MLX adapter knowingly lacked response-format
support, but `benchmark.py` requests a strict JSON schema for routing. Dropping that
option makes the routing control differ from the historical llama.cpp test, despite
unchanged messages. The unconstrained results above remain real observations, but
should not be treated as an equal-control routing comparison. This is a harness
limitation, not evidence that quantization alone caused the routing-score drop.

The corrected adapter enforces only the routing schema while decoding: a finite token
trie permits every independent skill/lane enum combination, both key orders, and
compact/default/indented JSON. It reads no expected route or tool answer. This finite
serialization subset is documented; it is not a complete general JSON grammar.
There is no post-generation cleanup and no constraint on tool-call arguments. Both
candidates will rerun the same40 accuracy requests with this control. Speed and soak
requests have no response_format, so their execution path is unchanged. The current
Gemma soak continues in the already-running original process; GPU self-checks and
corrected accuracy runs wait until it exits.

### Gemma DWQ RAM gate complete

The original full run exited1 because its unconstrained routing score was5/20; its RAM
component passed. Soak lasted603.055555 seconds, with120 samples
and the last sample at602.343687 seconds. All sampled pressure levels were1,
minimum free memory was23%, and there were no monitor/generation
errors. This does not erase the earlier immediate post-load pressure2 warning.

Peak RSS was7,916,339,200 bytes, while MLX peak allocation was
14,423,719,360 bytes. Metal allocations are not fully represented by process RSS;
these metrics overlap and must not be added. The final comparison reports MLX peak
allocation explicitly, with RSS and system pressure retained here. Peak sampled GPU
in-use memory during soak was14,786,101,248 bytes.

### Corrected Granite accuracy result

Schema-controlled accuracy exited0: **routing19/20, callable JSON20/20, exact14/20**.
Routing miss `r20` chose `algorithmic_coding`/`C`; the frozen expected skill differs.
All20 tool response choices are exactly identical to the unconstrained run, verified
by direct comparison. The control restores routing format; it does not repair arguments.
Every routing request records `response_format_enforced=true`.
Raw file: `.session/retest-20260909/granite-dwq-schema-quality-run.json`.
The schema adapter and synthetic checks are committed as `cc81339`.

## Final Lane A DWQ retest — 2026-09-10

The final routing scores use the restored finite JSON-schema control. Both models
reran all20 routing and20 tool-call cases; all tool response choices were identical
to their respective unconstrained runs. Original failed runs remain recorded above.

| candidate | quant | tok/s | routing | callable JSON | exact args | peak RAM |
| --- | --- | --- | --- | --- | --- | --- |
| Gemma 4 26B-A4B | 4-bit DWQ (published MLX) | 39.24 | 20/20 | 20/20 | 18/20 | 14.42 GB MLX |
| Granite 4.1 8B | 4-bit DWQ (local MLX) | 19.49 | 19/20 | 20/20 | 14/20 | 5.06 GB MLX |
| Qwen3.8-27B + CMoE | Not built: Metal unsupported | N/A | N/A | N/A | N/A | N/A |

**Recommendation:** Gemma DWQ is the best of these measured candidates by exact-argument
accuracy, then speed, but Lane A remains provisional. DWQ did not fix either existing
`t07`/`t12` error: both Gemma quants score18/20, while Granite scores14/20. No20/20-exact
replacement was found. The existing CLI remains on its Phase1 IQ3_S checkpoint; Phase2
was not started, and no model was promoted or deleted.

Both models pass the measured throughput, schema-controlled routing/callable-JSON,
and ten-minute steady-workload pressure gates. Gemma nevertheless produced pressure2
warnings immediately after **both** model loads; its subsequent ten-minute samples
were all normal. Those startup warnings are not erased by the steady-state pass.
The published Gemma artifact's DWQ training provenance remains publisher-claimed;
its immutable revision, file hashes and4-bit config were independently verified.

RAM in the comparison table means peak **MLX allocation**, not total process/system
memory. Peak RSS is recorded separately: Granite5.009GB, Gemma7.916GB. These figures
overlap and are not additive. The32K setting is an admission limit with dynamic KV:
maximum observed prompt-plus-response lengths were Granite1,063 and Gemma857 tokens.
A filled32K session was not stress-tested, so the table does not certify its RAM use.
Both models use8-bit KV quantized attention, not Flash Attention; the runtime exception
and exact cache behavior are recorded above.

Final evidence: `.session/retest-20260909/final-comparison.json`,
`granite-dwq-schema-quality-run.json`, `gemma-dwq-schema-quality-run.json`, plus the
separate speed/soak files already named. Both final accuracy processes exited0.
The shared corrected harness SHA256 is
`53bf03cc100da01dfa10c2363f2c04d030d37b13ab30af68772a2b8003110c29`.

Validation on 2026-09-10: synthetic routing-schema/KV/mask/context/timing tests, benchmark evaluator,
health-check regressions, and DWQ tied-head checks all pass. `./check.sh` exits0:
Python3.12.13, `Device(gpu, 0)`, wired limit20480,76.68GB free, unchanged recorded
19.48tok/s baseline, and verified03:00 backup registration with the documented
post-login command. The four protected root documents and `bench_cases.json` retain
their original hashes. No models, calibration data, research files or runtime logs are
tracked in Git; original Gemma IQ3_S weights are preserved.

### Handoff verification — 2026-09-12

Resumed from the completed comparison above; no model was loaded and no measurement
was repeated. An independent review confirmed the table against the raw accuracy,
speed and soak records, including memory and runtime caveats.
The frozen cases and corrected harness retain their recorded SHA256
hashes. Synthetic benchmark, routing-schema/KV/mask/context/timing, health-check and
DWQ tied-head checks pass again. Original Gemma IQ3_S weights remain present at
11,289,671,136 bytes, and the CLI still selects that checkpoint.

The current health check exits **1** because `iogpu.wired_limit_mb` has reset to **0**.
This is the intended failure behavior, not a new benchmark result. No sudo command
was run; before any further measurement the user must run and confirm:

```sh
sudo sysctl iogpu.wired_limit_mb=20480
```

The backup job was also absent after login. Re-registration with
`/Users/minhduc/Orbi/code/.venv/bin/orbi --schedule-backups` succeeded, and `./check.sh`
independently verifies the loaded 03:00 job. The wired limit is the only remaining
health-check failure; Python is 3.12.13 and MLX reports `Device(gpu, 0)`.

Three protected root documents (`CLAUDE.md`, `Orbiplan.md`, `Orbichecklist.md`) already
differed from the September 9 snapshot when this session resumed. No root document
was edited here; the session records its work in this code-local report as required
by the retest's write boundary.

### Cleanup audit and grammar correction — 2026-09-12

Read all958 lines of the updated root `CLAUDE.md` and the three companion planning
files. The new50-item future list is planning, not implemented features. The cleanup
did not remove a required Orbi dependency: Python3.12.13, `pip check`, the MLX GPU
import, the installed CLI entry point and llama.cpp b10809 all pass. No model was
loaded, downloaded, deleted or promoted during this audit.

The restored Flash-Next checkpoint is intact: all3 shards match their original
SHA256 hashes and total93,682,584,224 bytes. Full size/hash checks also pass for the
retained Gemma IQ3_S checkpoint, Harrier, the runtime archive, all10 files in the
Gemma DWQ manifest and the local Granite DWQ weight file. Evidence is in
`.session/retest-20260909/cleanup-audit-20260912.json`. The frozen benchmark cases
remain unchanged. User edits to the root documents were preserved and their hashes
stayed unchanged throughout this audit.

**Correction to the new grammar diagnosis:** Gemma's two exact-argument failures
are punctuation changes already present in the raw model output, not escaping
corruption introduced by a parser:

| case | field | expected decoded value | actual decoded value |
| --- | --- | --- | --- |
| t07 | query | `^def [a-z_]+\(` | `^def [a-z_]+\(.` |
| t12 | text | `The demo title is "Orbi 🌐".` | `The demo title is "Orbi 🌐"` |

Both values satisfy their unchanged tool schemas, which allow arbitrary strings.
Replaying all40 saved Gemma/Granite native tool frames through the current parsers
reproduces the recorded choices exactly; quote, backslash, newline and Unicode
round-trips also pass. Granite has six semantic mismatches, not one identical
failure shared with Gemma. The historical Gemma IQ3_S run has the same two
punctuation differences as its DWQ run.

[Upstream GBNF documentation](https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md)
describes constraints on output syntax and conversion of supported JSON schemas.
Our concrete counterexample above shows why a grammar derived from these schemas
cannot guarantee exact intended string values: it permits both the right and wrong
strings. Constraints may change generation and remain a useful experiment, but
**18/20 →20/20 is unmeasured, not a promised fix**. No grammar experiment or repaired
answer was substituted into the existing comparison. Added an evaluator regression
that keeps callable validity20/20 while scoring these punctuation errors18/20.
README and the config comment now make the provisional status explicit.

Current health differs from the earlier handoff: `./check.sh` exits0 with
`Device(gpu, 0)`, `iogpu.wired_limit_mb=20480`,133.97GB free at the first audit check,
and verified03:00 backup registration. No sudo or sysctl write was run here.
The live database and all5 existing nightly snapshots pass read-only integrity
checks; each snapshot has its markdown mirror. Deterministic memory tests pass,
including all three caps, scope isolation and delete/restore; CLI concurrency
controls, wired-limit/backup regressions and benchmark evaluator checks pass.
The preserved real recall result remains19/20 with its canonical fixture hash
verified, and the saved18-check real CLI result is intact. These historical model
scores were not re-measured after cleanup.

Two audit-command errors were resolved without changing data: a direct byte hash of
the pretty-printed recall fixture raised `AssertionError`; the original test hashes
canonical JSON (`sort_keys=True, ensure_ascii=False`), and that comparison passes.
The independent replay first raised `ImportError: cannot import name 'granite' from
'mlx_lm.tool_parsers'`; using the saved metadata's actual `json_tools` parser made
all replays pass. Neither error is a failed model gate or evidence of data loss.

## Recall and exact-argument fixes — 2026-09-13

Stage1 reserves the top3 semantic hits ahead of bootstrap/RRF, deduplicates, then
fills using the existing order. All12-item/4000-character/300-ms caps and scope
filters remain. Synthetic crowd-out, short-result, fallback and memory checks pass.
The full frozen recall suite still scores **19/20**, missing `recall-18`; worst
retrieval35.13ms. Unlike the old run, **Imani is now retrieved in position2**
(cosine0.481752, semantic rank2), but Gemma IQ3_S still replies `UNKNOWN`. The
retrieval omission is fixed; the end-to-end score is not improved. All20 semantic
queries, scope checks and delete/restore pass. Evidence: `.session/quality-fixes-20260913/`.

Greedy decoding was already active: installed MLX `generate_step` defaults to
argmax, and llama.cpp requests already sent temperature0. Both are now explicit
about top_p1; llama.cpp uses only its temperature sampler, MLX passes its verified
argmax sampler. The live llama.cpp chat slot confirms temperature0, top_p1 and
`samplers=["temperature"]`; effective parameters are saved for every recall answer.
The complete frozen DWQ run still scores routing20/20, callable JSON20/20 and
**first-pass exact arguments18/20** (`t07`, `t12` fail). Explicit greedy decoding
does not improve the score. Every tool response records effective argmax/top_p1.
Recall fixture SHA256 remains888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d
before/after; tool fixture remainsfdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d.
The requested semantic subagent hit its usage limit before writing; the parent
implemented and checked the fix locally. No root planning/research file was edited.

### Stage2 — one verbatim retry did not improve accuracy

The full frozen20-case recall suite remains **19/20**, with `recall-18` returning
`UNKNOWN` even though Imani's fact is present. Worst retrieval39.20ms; all caps,
scope and delete/restore checks pass, and the canonical fixture hash is unchanged.
All18 existing real CLI checks also pass with the new before-write guard.

The full Gemma DWQ tool suite is **18/20 first-pass, 18/20 after retry**, routing20/20,
callable JSON20/20. Exactly2 retries were attempted (`t07`, `t12`); each repeated
the same incorrect string and was rejected. Accepted calls18/20; benchmark process
exited1. No emitted string was rewritten into a passing answer. Raw first attempts,
source-derived diffs, retry requests/responses and remaining issues are preserved
in `stage2-tools.json` and `stage2-tools-quality.json` under the session directory.
The validator never reads a fixture answer key to construct feedback.

The shared source-copy check recognizes explicit colon-delimited exact facts,
newline-preserving instructions and the benchmark's explicit path/query delimiters;
it is not a general parser of arbitrary prose. The CLI validates `remember.text`
before saving, feeds back one diff, and fails nonzero if the correction still differs
or no corrected tool call arrives. Other file/search tools remain benchmark-only.
MLX retry history converts API argument strings to mappings and tool responses to
the installed Gemma template's native fields, without changing first-pass inputs.

A synthetic guard check initially raised `AssertionError` because it counted both
the rejection and successful execution result as rejection feedback; its assertion
now distinguishes those events. All guard/evaluator/MLX checks pass, including a
transport failure that cannot count as a successful retry. Editable installation
first failed with `pip._vendor.pyproject_hooks._impl.BackendUnavailable: Cannot import
'setuptools.build_meta'` when build isolation was disabled. Re-running with the
project's existing pinned isolated build backend succeeded; isolated imports and
`pip check` pass. No model or runtime dependency version was changed.

### Stage3 — regex validation rejects the error; accuracy remains unchanged

| Fix stage | Recall | Exact first-pass | Exact post-retry | Retries | Accepted tools |
| --- | --- | --- | --- | --- | --- |
| Semantic slots + explicit greedy | 19/20 | 18/20 | Not attempted | 0 | Not measured |
| One source-copy retry | 19/20 | 18/20 | 18/20 | 2 | 18/20 |
| Source-copy retry + regex examples | 19/20 | 18/20 | 18/20 | 2 | 18/20 |

Every stage ran all20 frozen recall cases and all20 frozen tool cases, plus
all20 routing cases. Stage3 routing and callable JSON remain20/20. Its benchmark
process exited1: the exact-argument gate still fails. `t07` still emits
`^def [a-z_]+\(.` instead of `^def [a-z_]+\(`; the emitted pattern compiles but
fails the required positive examples `def hello(` and `def _name(`. Negative
examples cover a class, an invalid identifier and wrong case. Both first attempt
and sole retry fail the copy and match checks. `t12` still omits the final period
from `The demo title is "Orbi 🌐".` on both attempts. Neither wrong call is accepted.
Validation checks compile/match in a one-second bounded subprocess; it never edits
an argument. Match examples are separate annotations, not changes to the fixture.

Final recall is19/20: `recall-18` still answers `UNKNOWN` despite the Imani fact
being retrieved in position2. Worst retrieval34.46ms; at most12 items and1798
rendered characters in this run. All caps, scope isolation,20 semantic queries
and delete/restore pass. These runs retain the existing evaluation split:
production IQ3_S + Harrier for recall, Gemma DWQ with the MLX adapter for tool
accuracy. They are not new speed/ten-minute RAM qualification runs, and no model
was promoted. Lane A remains provisional; Phase2 is still on hold.

Final verification passed deterministic memory, evaluator, source-copy/regex,
CLI rejection and MLX adapter checks. The real CLI suite passed all18 checks at
Stage2; no CLI logic changed at Stage3. `pip check` passes. `./check.sh` exits0:
Python3.12.13, `Device(gpu, 0)`, wired limit20480,132.63GB free, verified03:00 backup.
README now states the guard's behavior and unchanged scores.

Recall canonical SHA256 remains
`888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`
before/after every run. Tool fixture SHA256 remains
`fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`.
The final audit checks all60 saved first-pass tool requests against the frozen
prompts and schemas and verifies argmax/temp0/top_p1 for every tool attempt.
An initial audit raised `KeyError: 'fixture_sha256_after'`: Stage1 predates that
metadata field. The corrected audit checks its saved before hash, every saved
first-pass input and the current file; Stage2/3 also have matching after hashes.
No historical result file was rewritten to fill in missing metadata.

Raw Stage3 responses, retry diffs and failures are under
`.session/quality-fixes-20260913/stage3-tools-quality.json`; recall evidence is in
`stage3-recall.json` and the integrity audit is `final-validation.json` beside it.
The four root planning/memory files match their pre-run hashes. This session is
logged here, inside code/, respecting the explicit prohibition on editing them.

## Shared product prompt rules — 2026-09-13

The punctuation policy now applies to every Orbi generation, through a shared
message helper used before CLI context counting and by both inference adapters.
Frozen fixture system text remains intact as a prefix; the appended product policy
is logged in actual requests. No fixture or scoring edits were made. The actual
Gemma chat template was checked: the policy and original user prompt both survive
rendering. Prompt/context/evaluator/MLX checks and independent read-only review pass.

The punctuation-only full rerun scores recall19/20 (`recall-18`: `UNKNOWN`),
routing20/20, callable JSON20/20, exact18/20 first-pass and18/20 post-retry. Both
`t07` and`t12` repeat their punctuation errors on the sole retry; accepted18/20,
benchmark exit1. The rule did not improve either error. Caps and restore checks
pass; worst retrieval34.40ms. Separate diagnostics remove each answering fact
from its retrieved context: all20 return `UNKNOWN`. These diagnostics do not add
passes to the frozen recall score. Evidence: `.session/prompt-rules-20260913/punctuation/`.
Both fixture hashes and the entire `test_recall.py` file match their before hashes.

### Meaning-based memory rule — final frozen-suite results

The shared product policy now recognizes answers expressed in different words,
including responsibility implied by a named role. It explicitly preserves UNKNOWN
when a related topic does not supply the requested fact. No retrieval, fixture,
scoring, sampling, retry-count or cap changes accompanied this second rule.

| Product prompt | Frozen recall | Exact first-pass | Exact post-retry | Retries | Separate abstention |
| --- | --- | --- | --- | --- | --- |
| Punctuation rule | 19/20 | 18/20 | 18/20 | 2 | 20/20 |
| Punctuation + meaning-based memory rule | 20/20 | 18/20 | 19/20 | 2 | 20/20 |

Both full20-case suites were rerun after each policy change, plus the20 routing
cases. Final recall has no failures: `recall-18` now returns `Imani Tran`, and all19
previously passing cases remain correct. Each separate abstention diagnostic
removes the answering fact and retains the other retrieved blocks; all20 still
return UNKNOWN. Those results are not counted as additional recall successes.
The 12-item/4000-character/300-ms caps remain unchanged; observed maxima are12
items,1798 rendered characters and34.57ms. Scope and delete/restore checks pass.

Final tools still score routing20/20 and callable JSON20/20. First-pass failures
remain `t07` (adds a period to the regex) and `t12` (drops the exact fact's period).
Each receives only one retry. With both prompt rules present, `t12` copies the
full fact correctly on retry; **t07 still fails**. Its emitted `^def [a-z_]+\(.`
compiles but fails the intended positive targets `def hello(` and `def _name(`.
The source-copy and regex checks reject it on both attempts. Exact post-retry and
accepted calls are19/20; benchmark exit1. No argument was automatically rewritten
or credited to the first pass. The remaining failure is measured noncompliance
with the punctuation rule, despite that rule being supplied in the system prompt.
Lane A remains provisional and Phase2 remains on hold.

As in the preceding run, recall uses the product IQ3_S runtime with Harrier;
tool accuracy uses Gemma DWQ via MLX. These are accuracy measurements, not fresh
speed or ten-minute memory-pressure qualification runs. All18 real CLI checks
pass with the final product prompt, including actual remember/recall calls,
streaming, continuation, pipes, cancellation, context overflow and crash controls.
Focused prompt/context, evaluator and MLX adapter checks passed; `pip check`
passes. `./check.sh` exits0: Python3.12.13, `Device(gpu, 0)`, wired limit20480,
131.48GB free and verified03:00 backup registration.

Before/after canonical recall SHA256:
`888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`.
Before/after tool fixture SHA256:
`fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`.
The entire `test_recall.py` file is also byte-for-byte unchanged. The audit checks
all saved first-pass user prompts and tool schemas against the frozen cases,
and verifies that only the shared product policy was appended to system text.
HTTP recall slots confirm temperature0/top_p1/temperature-only sampling; every
MLX attempt records argmax/temp0/top_p1. Raw first/retry responses, policy text and
hashes, separate abstention results and final integrity checks are preserved in
`.session/prompt-rules-20260913/`; `final-audit.json` summarizes both stages.
README reflects the final scores. The four root documents, memory implementation
and cap configuration retain their before hashes; this session is logged here.

## Actionable regex retry diagnostic — 2026-09-14

| Measurement | Result |
| --- | --- |
| Exact arguments, first-pass | 18/20 |
| Exact arguments, post-retry | 20/20 |
| Retries | 2 total; one each for t07 and t12 |
| Accepted calls | 20/20 |
| Routing / callable JSON | 20/20 / 20/20 |
| Frozen recall / separate abstention | 20/20 / 20/20 |

The shared regex validator now includes the emitted pattern, each failing target,
and a specific explanation in retry feedback. It recognizes a terminal wildcard
using the pinned Python 3.12 parser and verifies the explanation by matching the
unchanged pattern against the target with one extra character. This diagnostic
stays inside the existing one-second subprocess limit. It does not change the
pattern, the intended targets, the scorer, the system prompt or the retry limit.
Synthetic checks cover escaped/class/optional dots, comments, excluded targets,
and a lookahead counterexample where appending a character does not prove that
the final wildcard consumed it. Focused checks and read-only review passed.

`t07` first emitted `^def [a-z_]+\(.`. Its single retry received the explanation
that the trailing dot requires another character after `(`, with `def hello(`
and `def _name(` as the failing targets. **Gemma itself then emitted
`^def [a-z_]+\(`**, visible in the retained native response, and passed exact
arguments plus regex validation. `t12` also corrected its missing period on its
single retry. No case fails after retry; first-pass accuracy remains 18/20.
The full tool benchmark exited 0. No deterministic repair or additional model
attempt was used to manufacture either pass.

Both full frozen suites and all 20 target-removed abstention diagnostics were
rerun. Recall remains 20/20 with no regression; every absent-answer diagnostic
returns UNKNOWN. Retrieval, scope and delete/restore checks pass, with observed
maxima of 12 items, 1798 characters and 41.86 ms. The 12/4000/300 caps are unchanged.
Recall still uses the product IQ3_S runtime plus Harrier; tool accuracy uses the
existing Gemma DWQ MLX adapter. No speed or ten-minute memory gate was re-measured.
`./check.sh` exits 0: Python 3.12.13, `Device(gpu, 0)`, wired limit 20480,
129.78 GB free and verified 03:00 backup registration.

Both fixture SHAs match before and after:

- Recall: `888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`
- Tools: `fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`

The entire `test_recall.py`, product system prompt, inference adapters, scorer,
memory implementation, cap configuration and four root documents are unchanged.
All 20 first-pass tool requests match the preceding run byte-for-byte after JSON
serialization. Temperature 0/top_p 1 and effective greedy sampling were verified.
Raw responses, exact retry feedback, policy and integrity evidence are under
`.session/regex-diagnostic-20260914/`; `final-audit.json` summarizes the results.
The raw tool log also retains a macOS diagnostic, `MallocStackLogging: can't turn
off malloc stack logging because it was not enabled.` It did not stop generation
or cause a failed check. README reflects the measured post-retry success; no model
promotion or Phase 2 implementation was performed.

## Phase 2 routing — initial dispatch failure, 2026-09-14

The unchanged coarse classifier scored **20/20**, but the first product routing
implementation scored **15/20** on final lane selection. All 20 requests went
through the installed Gemma IQ3_S runtime, the complete catalog selection and
SQLite decision log. The five misses were:

| Case | Expected lane | Actual lane/model | Cause |
| --- | --- | --- | --- |
| r10 | B | C / Qwen3.6-35B-A3B | Generic catalog embedding default overrode the plan's dedicated specialist |
| r11 | B | C / Kimi K3 | Catalog has no translation leaf; nearest correspondence leaf selected a giant |
| r15 | B | C / InternVL3.5-241B-A28B | Generic grounding default overrode the plan's smaller grounding specialist |
| r16 | B | C / Qwen3.6-35B-A3B | Generic reranking default overrode the plan's dedicated reranker |
| r17 | C | B / Qwen3.5-27B | Named minimum-viable proof model moved the request to B |

The 302-leaf catalog is a research snapshot, not ground truth. Dispatch was
corrected to honor the explicit `Orbimodels.md` specialist job models for B
operations where no named leaf alternative exists. Named minimum-viable
alternatives retain priority; the original catalog pick and the reason for any
override remain in each decision. The r17 outcome is not forced back to C to
match the fixture. This section records the failed run; a later result must be
measured separately.

Initial routing latency was 304.19 seconds across 20 decisions (15.21 seconds
mean), excluding answer generation. The bounded three-call classifier does not
meet the plan's unmeasured 0.2-second estimate. Wired limit was 20480 before the
run. Raw decisions, responses, outcomes and token counts are preserved at
`.session/routing-8fffc4ae3b8241128c2c73e86b3c41dd/results.json`.

No B/C weights were downloaded or executed. Unavailable asks returned exit 3;
their `succeeded` field is null. Frozen fixture hashes stayed unchanged.

## Phase 2 routing — corrected dispatch, 2026-09-14

Final product routing scores **19/20** on the full frozen r-cases; the existing
coarse classifier remains **20/20**. Final scoring requires both the expected
category and lane, and separately records each score. **r17 is the only miss**:
the frozen case expects C, but the selected proof leaf explicitly names
Qwen3.5-27B as its minimum-viable choice, so the capacity default sends it to B.
Its suitability is not independently proven by this routing test. The smaller
model preference was preserved; the fixture was not edited to count it as a pass.

All other requests selected the expected lane. Six A requests completed local
generation and recorded `succeeded=1`. Fourteen B/C decisions returned truthful
not-installed output and exit 3, with `succeeded=null`. No specialist inference
or replacement weights were used. The actual model was the installed Gemma
UD-IQ3_S checkpoint, with the unchanged `--cache-ram 0` runtime configuration.

Measured mean routing latency is **15.71 seconds**, excluding answer generation;
the largest individual classification prompt was 1,073 tokens. All three calls
remain within the existing 4,096-token context. This is a bounded implementation,
not verification of the plan's 0.2-second estimate or of specialist model fit.
Wired limit was confirmed 20480 before the run. Raw final evidence:
`.session/routing-6f3eba70b3df406993fb651a734c426b/results.json` and
`.session/phase2-20260914/routing-final.json`.

One actual persisted decision:

```text
task: a1543a83e56c4fdbaf1ef563e65d85a2
request: extract the line-item table from a scanned invoice
skill: d04.s01.l06 — receipt/invoice line-item parsing
lane: B
model: PaddlePaddle/PaddleOCR-VL-1.6
status: not_installed
succeeded: null
```

The classifier identifies scanned-document extraction, then the specific invoice
leaf. Dispatch uses the explicit `Orbimodels.md` OCR specialist, preserves the
catalog's GLM-OCR pick and reasoned-default status, and records why the plan
default took precedence. This is inspectable provenance, not a newly verified
model-quality result. Decisions are project-scoped in the CLI and included in
SQLite backups; deterministic controls verified restore, failure, cancellation,
crash recovery and deferred-job persistence.

## Phase 2 Phase 1 regressions — 2026-09-14

| Suite / backend | First-pass | Post-retry | Retries | Result |
| --- | --- | --- | --- | --- |
| Frozen recall / IQ3_S + Harrier | 20/20 | n/a | 0 | Pass |
| Answer-removed abstention / IQ3_S | 20/20 | n/a | 0 | Pass |
| Frozen tools / installed IQ3_S | **17/20** | **20/20** | 3: t07, t09, t12 | Post-retry gate passes |
| Frozen tools / recorded DWQ MLX backend | **18/20** | **20/20** | 2: t07, t12 | Recorded scores preserved |

Both tool backends also score callable JSON20/20 and coarse routing20/20.
The installed IQ3 first-pass result here is lower than the18/20 stated in the task.
The adjacent18/20 run belongs to DWQ, but the older
`.session/gemma-iq3-nocache-quality.json` also records IQ3 at18/20.
These are separate measurements; it was incorrect to imply IQ3 never scored18/20.
IQ3 additionally dropped the final period in t09's exact fact; its single retry
restored it. Neither backend has a remaining post-retry failure, and no emitted
argument was repaired in code.

Recall includes the Imani Tran case, all scope/cap checks, and actual deletion
and restoration of the isolated30-row database with identical vectors. Maximum
retrieval was43.30ms; all requests stayed within12items/4000chars/300ms. All20
separate absent-answer checks returned UNKNOWN. All18 existing real CLI/control
checks and the new installed-command checks passed (forcedA/pipes, auto specialist
preview, explanation/inspection, and deferredC submission). Phase1 memory, caps,
system policy, runtime and stream implementation remain unchanged from779d2ef.

The combined test runner exited1 **after** IQ3 inference completed while saving
its result: `OSError: Could not verify /Users/minhduc/Orbi/code/.session/phase2-20260914/final/product-iq3-tools.json.tmp`.
Regex example tuples become JSON arrays, so the writer's strict Python equality
check failed. The complete raw JSON was recovered, all20 prompts/schemas and
scores verified, and identical data published after normalizing metadata to
JSON-native lists. No model output was altered or attempt repeated. The ignored
harness was fixed; recovery SHA/evidence is in `artifact-save-recovery.json`.
The remaining DWQ suite was run separately and exited0. The final audit verifies
all results independently instead of treating that first runner exit as a pass.

Raw evidence is under `.session/phase2-20260914/final/`:
`recall.json`, `abstention.json`, `cli.json`, `product-iq3-tools.json`,
`tools-quality.json`, and `tools.json`; new CLI transcripts are in the sibling
`commands/results.json`. All model work ran offline; no weights were downloaded.

`./check.sh` exits0: Python3.12.13, `Device(gpu, 0)`, wired limit20480,
122.40GB free on the data volume, and verified03:00 backup registration.
Before/after fixture SHA256 values are unchanged:

- Recall: `888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`
- Routing/tools: `fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`

`test_recall.py` is byte-for-byte unchanged. The three spec documents and skill
source also retain their before hashes; CLAUDE.md was appended and committed in
the separate root repository as work progressed. The source count302 versus341,
missing translation leaf, and15.71s measured routing versus the plan's0.2s estimate
remain explicit limitations, not silent spec edits.


## Routing latency diagnosis and rejected trials — 2026-09-20

A full20-case instrumented repeat of the original implementation measured
**15.2867s mean**, excluding answer generation. Wired20480; IQ3_S; original
single-slot4K runtime with `--cache-ram 0`. No model downloads.

| Component | Mean per decision |
| --- | ---: |
| Prompt processing, three calls | 11.5010s |
| Classification generation, three calls | 3.7458s |
| Template/token-count HTTP preflights | 0.0240s |
| Construction, import and dispatch | 0.00039s |
| Remaining HTTP/validation overhead | 0.01563s |

The three prompts average1003.15,1047.15 and456.45 counted tokens; native server
prompt counts differ slightly with template special tokens. The total native
processing average is2509.75tokens; generation averages101.45tokens, much of it
leaf-explanation prose. The complete302-leaf catalog was **not** being sent in
those prompts: the existing implementation used category,39-group and≤10-leaf
menus. An audit hook saw the catalog bytecode open only on the first request.
Configuration read took0.493ms; warm runtime ownership/health checks averaged
21.404ms. Cold generation+embedding startup took11.907s once, not on every
classification. Evidence: `.session/routing-latency-20260915/baseline-profile.json`
and `baseline-summary.json`.

The measured alternative uses one compact catalog prompt, full category names,
and a short constrained category/leaf result. It does not generate explanatory
prose: inspection shows the actual classification, category rule, source pick,
minimum alternative, availability and dispatch rule. Source verification labels
remain historical claims; leaf matches are explicitly unverified model outputs.
The unchanged hierarchy handles requests too long to fit the compact menu in4K;
requests are never silently truncated. Both paths can report an unmatched leaf
and retain the operational category. Explicit `--lane a` skips classification.

| Trial | Result | Disposition |
| --- | --- | --- |
| Compact array, cache0, consecutive routing | category19/20; first22.57s; later19 mean1.008s | Rejected: r07 category miss and no protection against answer-prefix eviction |
| Native cache256MiB | ~17s decisions; state464.6MiB exceeds cap | Rejected: native cache explicitly skipped the oversized state |
| Native cache512MiB, one checkpoint | ~18s decisions; restored state but no reusable prefix | Rejected: sliding-window state could not rewind to the changed user suffix |
| Cache768MiB, three checkpoints, letter codes | category15/20 | Rejected: category letters confused with lane letters |
| Same cache, full category names | category20/20 and final lanes20/20; all20 mean1.8359s; subsequent19 mean0.9696s | Short-answer interleaving prototype only; first uncached classification remains slow |

Every request in the last prototype was followed by an unrelated generated
answer on the same slot. That short-answer workload does **not** establish the
latency of longer product replies. The first full product run exposed repeated
prefix eviction after longer Lane A answers: mean5.1291s over19 completed
classifications. It also found a client parser bug: r14 emitted the valid
`model3d_generation:168`, but the parser rejected digits in category names with
`ValueError("Invalid catalog classification: 'model3d_generation:168'")`.
Result19/20; the failed decision is not counted as a measured latency success.
The parser now accepts digits, has a control test for that category, and a full
product rerun follows. Raw failed run:
`.session/routing-7584ca3e995446628d6a39f765157a6b/results.json`.

The768MiB/three-checkpoint experiment observed memory for602.504s:
peak model RSS12.754GB, pressure levels1(normal) and2(warning).
This is **not** an all-normal pressure pass. No model throughput or memory
qualification should be inferred from the short routing prototype.
Evidence: `cache-memory.json` in the latency directory.

### r17 and prompt-regression findings

r17 is a real over-specific selection, not a demonstrated stale fixture. Its
adversarial online-matching proof is not covered by the narrow propositional/
first-order-logic leaf or its QMFOLBench citation. The smaller-model rule applies
after matching the operation; it does not justify that mismatched downgrade.
The full-name prototype emits no matching leaf for r17 and retains formal
reasoning/C. No fixture or source/spec edit was made. Other proposed leaf
associations are still imperfect (for example text translation associated with
transcription);20/20 category/lane accuracy is **not**20/20 leaf accuracy.

Old IQ3 first-pass18/20 versus September14 IQ317/20 differs only on t09.
Routing menus do not enter the tool suite. The tool prompt gained205 shared
policy tokens and explicit temperature-only sampling was added between those
historical runs, so that comparison alone does not isolate quantization loss.
The new same-runtime IQ3/IQ4 comparison will hold prompts and flags constant.

Two attempted exact-copy prompt clarifications were measured and removed:

| Product-policy trial | Recall | Abstention | Tools first-pass | Post-retry |
| --- | --- | --- | --- | --- |
| Shared extra scope/tag copy instruction | 19/20: recall-18 UNKNOWN | 20/20 | 18/20 | 20/20 |
| Extra instruction only with tools enabled | 20/20 | 20/20 | 17/20 | 20/20 |

Neither met the combined requirements. The original shared policy and original
benchmark prompt handling are restored. Regex diagnostics/retries and all memory
caps remain unchanged. Raw evidence: latency directory `policy-fix/` and
`scoped-policy/`; both complete suites retain unchanged frozen fixture hashes.


### Corrected product routing gate — 2026-09-20

The full frozen product-path suite now scores **20/20 category and final lane**,
including r14 after the digit-parser fix and r17 as unmatched formal reasoning/C.
Actual average routing time is **5.0571s** over all20 requests:15 cached decisions
average **0.8882s**, while5 require catalog prefill. Longer real Lane A replies
can evict the prefix, unlike the short interleaved answers in the prototype.
This is the achieved product result, not a general sub-second claim. Per the
user's new instruction, freeze the768MiB/three-checkpoint configuration and
compare quantizations without further latency tuning.

Evidence: `.session/routing-988b48c6691f42ccb1dfbb4a478149e8/results.json` and
`.session/routing-latency-20260915/product-routing-summary.json`.
All20 decisions use the single-call path on these short frozen inputs; no B/C
model executes. Both fixture files are unchanged. The hierarchy and its unmatched
outcome, forcedA bypass, invalid outputs, failure/cancellation/crash persistence,
backup restore and project-scoped inspection pass deterministic controls.


### Controlled IQ3 baseline; IQ4 blocked by reset wired limit — 2026-09-20

The completed same-runtime comparison baseline used Gemma UD-IQ3_S, llama.cpp
b10809, mmap, Flash Attention, Q8 KV, context4096, one slot, cache768MiB and
three checkpoints. Production prompts/config/source hashes were frozen.

| Quant | tok/s | Product routing | Callable JSON | Exact first-pass | Post-retry | Peak RSS | Memory pressure |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| UD-IQ3_S | 26.637 | 20/20 | 20/20 | 17/20 | 20/20 | 13.092GB (12.193GiB) | 600.524s:25 normal,96 warning samples; no critical samples |
| UD-IQ4_XS | Pending | Pending | Pending | Pending | Pending | Pending | Not started |

IQ3 first-pass failures are t07/t09/t12; all pass after one retry each. Recall
and answer-removed abstention are both20/20. Actual product routing averages
5.0554s over all20 decisions;15 catalog-cache hits average0.8315s and5 are
misses. This agrees with the preceding product gate, not a blanket sub-second
claim. The ten-minute observation fails the harness's all-normal pressure
criterion: pressure2 is a warning, not a clean memory pass. No critical pressure
or benchmark error was recorded. Peak RSS is the monitored generation process,
not total system RAM.

Evidence: `.session/iq4-comparison-20260920/iq3/` includes raw outputs, native
timings, memory samples, protocol/config/source hashes and verified shutdown.
Before/after wired limit was20480 for that completed run. Frozen bench SHA
`fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`
and canonical recall SHA
`888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`
were unchanged.

On resuming at20:06 local time, the live read returned exactly
`iogpu.wired_limit_mb: 0`. IQ4 has not started; no adoption decision or
`orbi.toml` change was made. The user must run
`sudo sysctl iogpu.wired_limit_mb=20480` and confirm before measurement resumes.
No sudo command was executed by the agent.

### Completed IQ3 versus IQ4 comparison — 2026-09-20

After the user restored the wired limit, the live read returned 20480 before
IQ4 began; it remained 20480 at the end. IQ3 had already finished and stopped.
Both runs used the same frozen source/config/prompt protocol, native runtime,
greedy decoding, context 4096, Q8 KV, cache 768MiB and three checkpoints. The
generation model path selects each quant; test data directories are isolated per run. No downloads,
MLX substitution, routing tuning, fixture edits or argument repairs occurred.

| Candidate | tok/s | Product routing /20 | Callable JSON /20 | Exact args first-pass /20 | Post-retry /20 | Peak generation RSS | 10-minute memory pressure |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Gemma UD-IQ3_S | 26.637 | 20 | 20 | 17 | 20 | 13.092GB | 600.524s; 25 normal, 96 warning; 0 critical |
| Gemma UD-IQ4_XS | 24.002 | 20 | 20 | 18 | 20 | 3.974GB | 600.573s; 48 normal, 73 warning; 0 critical |

These are measured process RSS peaks, **not total unified-memory footprints**.
Device-wide GPU memory in use peaked at 14.211GB for IQ3 and 16.567GB for IQ4;
allocated GPU memory peaked at 15.157GB and 17.413GB. The lower IQ4 process RSS
does not establish lower model RAM use. Measurements were sequential, separated
by a user reboot/restoration; foreground workload and OS memory accounting were
not controlled. Both observations have 121 samples at approximately 5-second
intervals, no monitor errors, and fail the harness's all-normal memory criterion.
The harness exits 1 for a failed gate; a completed measurement is not a passed gate.

**t09 passes first-pass on IQ4.** For the identical request/schema/system prompt,
IQ3 emitted `I prefer replies in Vietnamese` and IQ4 emitted
`I prefer replies in Vietnamese.`. The required final period is present in IQ4.
IQ3 first-pass failures: t07/t09/t12, with 3 retries; IQ4: t07/t12, with 2 retries.
Every retry is reported separately; both post-retry suites score 20/20.
The original coarse routing benchmark also remains 20/20 on both.

**Decision: retain IQ3; do not adopt IQ4 yet.** IQ4 meets the tool-improvement
and >15 tok/s conditions, but violates the mandatory recall non-regression gate:
IQ3 recall 20/20, IQ4 recall 19/20. IQ4's only miss is recall-18,
`Who owns the go-live checklist?` → `UNKNOWN`, although the Imani Tran release
coordinator fact appears second in retrieved memory. This is an answer failure,
not a missing retrieval. Abstention remains 20/20 for each quant. No claim that
recall is unchanged is warranted. Production `orbi.toml` and setup artifacts
remain on IQ3; both existing GGUFs are retained. No prompt fix was folded into
this quantization comparison.

All 20 first-pass tool request objects are byte-for-byte identical across quants.
Recall uses generated timestamp/UUID project directories in the retrieved text,
so its complete requests are not byte-identical. After normalizing only those
ephemeral paths, all 20 requests and retrieved item ordering/text match; effective
greedy sampling matches throughout. The observed recall failure blocks adoption,
but this comparison alone cannot prove quantization caused it rather than
sensitivity to the changed directory text.

Product routing remains 20/20 categories/final lanes for both, with no missed
r-cases. The complete 20-decision mean changes from 5.0554s (IQ3) to 4.9978s
(IQ4), a measured difference of −0.0576s. Each has 15 substantive catalog-cache
hits and 5 misses; hit-only means are 0.8315s and 0.8165s. These single runs do not
establish a statistically significant latency improvement or a sub-second
overall router. No new leaf-accuracy claim is made.

Memory retrieval retains 12 items / 4000 chars / 300 ms caps and correct scopes on both;
worst measured retrieval 35.581ms (IQ3) and 89.732ms (IQ4). Both delete-then-restore
tests preserve all 30 rows/vectors and snapshot hashes. Both fixture hashes were
verified unchanged before and after each run:

- Recall canonical SHA256: `888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`.
- Routing/tools SHA256: `fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`.
- `test_recall.py` byte SHA256: `ae83425c9cd3a569403c50d7ee95eb6a90a3569d1062856aecf50af52fb2387d`.

Flash Attention was enabled at context level: both native commands specify
`-fa on` and Q8_0 V cache, and the pinned runtime rejects quantized V when FA
is disabled, including a second check after graph reservation. This is stronger
than checking the requested flag, but is not a per-kernel device trace.
[Pinned native initialization](https://github.com/ggml-org/llama.cpp/blob/5266f24da/src/llama-context.cpp#L416-L423).
IQ4_XS is a GGUF quant, **not DWQ**; the spec's literal DWQ procedure remains
inapplicable to this unchanged llama.cpp path. No new 32K-context qualification
is claimed from the frozen 4K runtime comparison.

Raw evidence and verified shutdowns: `.session/iq4-comparison-20260920/iq3/`
and `iq4/` (`summary.json`, `tools.json`, `recall.json`, `abstention.json`,
`routing.json`, `memory.json`, `runtime.json`, `protocol.json`, `verification.json`).
The shared harness SHA256 is
`280a508d70c077d5603663ed58c92d83851b11500bf08a55c2928f74f367a603`.

Final health initially exited 1 with exactly:
`WARNING: Nightly backup registration is missing or mismatched. Run: /Users/minhduc/Orbi/code/.venv/bin/orbi --schedule-backups`.
Re-registered the existing 03:00 backup job using that command; subsequent
`./check.sh` exited 0: Python 3.12.13, MLX `Device(gpu, 0)`, wired 20480,
126.15GB free, backup registration verified. Logs: `final-health.log` and
`final-health-restored.log` in the comparison directory. This health pass does
not override either benchmark's memory-pressure failure or IQ4's recall miss.

### Controlled fixed-path recall-only rerun — 2026-09-21

**Branch 2: keep IQ3_S.** The earlier directory confound is removed. The full
frozen recall suite produces the following result under identical inputs:

| Quant | Recall | Misses | Retrieved or answering failure? |
| --- | ---: | --- | --- |
| UD-IQ3_S | 20/20 | None; recall-18 answers `Imani Tran` | None |
| UD-IQ4_XS | 19/20 | recall-18 answers `UNKNOWN` | Answering: Imani Tran is retrieved second |

Both use the exact same project paths under
`/Users/minhduc/Orbi/code/.session/recall/20260921T000000-00000000/`:
`project-aurora` and `project-borealis`. The unchanged frozen `test_recall.main()`
runs twice, with only its own directory-generation clock/UUID references held
constant. The first test directory is archived before recreating the same path
for IQ4. Both models start in fresh servers and answer cases 01–20 in the same
order. All 20 complete native request objects and effective sampling parameters
are exactly equal across quants, without path normalization. Each IQ4 request
input is checked against IQ3 before inference; the final recorded native bodies
are also checked. The harness's legacy ≥17 threshold/exit 0 is not a 20/20 claim.

Both runtime commands match the prior frozen comparison except model filename:
one slot, context 4096, mmap, Flash Attention, Q8 K/V,
`--cache-ram 768 --ctx-checkpoints 3`. Wired limit 20480 was confirmed before
each quant and after both. Prompts, system rules, fixtures, caps and router
configuration are unchanged. All caps/scope/restore checks pass; worst retrieval
42.080ms (IQ3) and 46.169ms (IQ4). No tool, speed, routing, abstention or ten-minute
soak suite was rerun. Previously observed pressure warnings are a shared issue,
not a tiebreaker; RSS did not enter this verdict.

Both frozen SHAs were verified unchanged before and after:

- Recall: `888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`.
- Routing/tools: `fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`.

`orbi.toml` remains on IQ3_S. IQ4's previously measured tool gain and 24.00 tok/s
still stand, but the fixed-path recall result selects the user's second branch.
Evidence: `.session/recall-fixed-20260921/` contains the verified harness,
protocol, fixed fixture, per-quant raw results/requests/runtime commands,
archived test databases, shutdown records, summary and final verification.

## Phase 3 permissions — implementation and controls, 2026-09-21

The permission boundary is enforced in Python, with a closed typed executor and
an explicit `orbi tool NAME JSON` CLI. Existing model schemas, `SYSTEM_RULES`,
per-turn prompt, routing/catalog, IQ3 model and frozen server flags are unchanged.
No model downloads, weight edits, quantization comparisons or Phase 4 execution
were performed. `orbi.toml` remains on the normally aligned instruction model;
no content/topic refusal filter was added. Memory tools retain their existing
behavior and now receive decision rows.

| Phase 3 item | Control result |
| --- | --- |
| 1 Auto | Read/list/Git status execute and log; absent/denied directory reads fail visibly; Git status does not refresh the index |
| 2 Confirm | Write/edit/local-artifact install/staged commit show exact changes before terminal approval; decline, absent terminal and changed target fail |
| 3 Never | Closed action set rejects recursive delete, sudo, force-push, arbitrary interpreters, unknown actions and out-of-root writes |
| 4 Hard test | **PASS:** `SYSTEM_RULES=''`, all system messages omitted, recursive-delete tool emitted into the real `_run_turn` dispatcher; sentinel unchanged, Never refusal persisted |
| 5 Permissive | Permission decisions depend on capability/path, not topic; arbitrary textual fixture content can be written with approval |
| 6 Normal model | Original instruction-model config and prompt retained; no abliterated model or weight modification |
| 7 Web data | Injected fixture stays an inert `untrusted_web` value and dispatches no action; this is a data-boundary check, not measured model injection resistance |
| 8 Audit | SQLite `orbi_permissions` records outcomes, previews and reasons; same-project inspection and interrupted-decision recovery pass |
| 9 Nuke | Hardcoded single root, default dry-run, exact terminal word, realpath checks and throwaway deletion pass; live destructive path never exercised |
| 10 Computer guard | Named event, AppleScript, screen-capture and Python input APIs fail closed, as do obfuscated/interpreter command forms |

The install operation is deliberately limited to copying an existing local
artifact with an exact byte preview. It does not run pip/npm, package hooks,
scripts, dependency resolution or binaries. Text previews include complete
before/after strings as escaped JSON; binary previews carry base64 rather than
a hash-only approximation. Commit uses a snapshot of the approved index and an
atomic comparison against the reviewed parent; executable Git helpers are
disabled. Git operations and mutation targets are scoped to code/. Existing
local branches are supported; linked Git metadata/common directories are refused.
These limits preserve the Phase 4 agent-layer boundary.

The initial live nuke dry-run exited 0 and listed **14,814** candidates; every
listed candidate's realpath was under `/Users/minhduc/Orbi/code`. It rejected
**3 outward symlinks** and excluded their ancestors from deletion candidates.
On this live tree, destructive nuke therefore refuses until those links are
resolved. This is an explicit guard result, not a claim that live deletion was
tested or could currently succeed. Only temporary trees were actually deleted.
The audit database and all SQLite sidecars are checked before initialization;
refusals cannot first write through an outward database symlink. Nuke emits its
final audit to stdout because successful deletion intentionally erases its DB.

### Failed intermediate checks, preserved

- `permissions-run1.log`: test harness accidentally mocked the shared subprocess
  module and blocked the legitimate audit-owner `ps` lookup. Isolated that mock.
- `permissions-run2.log`: `/usr/bin/git` exited **69**, Xcode licence unaccepted.
  Used the existing fixed `/opt/homebrew/bin/git` (**2.55.0**); no sudo/system change.
- `permissions-run3.log`: the test verification helper inherited intentionally
  hostile `GIT_DIR`. Isolated the helper while retaining the hostile executor test.
- Original validator unit harness failed with `TypeError` because its mock Task
  had no concrete SQLite path. Adapted only temporary DB/mock setup in
  `test_tool_validation.py`; original cases, assertions and scoring are retained.
  Frozen `bench_cases.json`, `test_recall.py`, `test_cli.py` and `test_routing.py`
  are unchanged.
- A real PTY check failed with `io.UnsupportedOperation: File or stream is not
  seekable` for `/dev/tty` in `r+` mode. Separate read/write handles fixed the
  actual confirmation path. A permanent real-PTY check now verifies that `yes`
  cannot substitute for nuke's `orbi` confirmation.
- Independent source review found case-insensitive `.GIT` protection, Git
  `commondir` redirection, incomplete submodule diffs, symbolic ref redirection
  and nuke audit-path prevalidation gaps. Fixed before regression measurement;
  focused path/metadata controls cover the escapes. No destructive exploit was
  run against the live vault.

The corrected permission suite passes **14 groups**. Existing deterministic
routing, CLI/control, source-copy/regex, benchmark evaluator, memory and health
controls pass. Evidence lives in `.session/phase3-20260921/`, including per-run
logs, `permissions-results.json` and the live `nuke-dry-run.json`.

### Explicit deferrals

- The computer-use Never guard is a **deliberate Phase 3 placeholder, not a
  content/policy decision**. Phase 4C replaces it with tree-first routing and
  per-action permission checks. No computer mode was built.
- The four inert catalog leaves `d02.s05.l01`, `d02.s05.l02`, `d04.s05.l04` and
  `d04.s05.l05` remain unchanged. Phase 4C will measure and correct their
  preferred picks; Lane B is not installed.
- Guard-model injected-page detection is deferred to Phase 4: the Group 13 web
  fetcher is not built and Granite Guardian 4.1 8B is not on disk. No download.
- Group 9 hooks and the general agent layer remain Phase 4 work. Enforcement in
  this phase is direct code, not hooks or a model instruction.

The live no-drop model/CLI regression results follow below.

### Live regression results and runner correction — 2026-09-22

The combined live runner preserved these completed scores:

| Gate | Result |
| --- | ---: |
| Recall | 20/20 |
| Answer-removed abstention | 20/20 |
| Coarse benchmark routing | 20/20 |
| Real product category / final lane | 20/20 / 20/20 |
| Callable JSON | 20/20 |
| Exact tool arguments, first-pass | 17/20 |
| Exact tool arguments, post-retry | 20/20 |

First-pass misses remain **t07/t09/t12**, one successful retry each. Recall uses
the same fixed project paths as the accepted IQ3 baseline; all 20 complete native
request objects are exactly equal, without path normalization. Retrieval, scope,
and delete/restore checks pass. Full server commands equal the frozen prior IQ3
commands. Both frozen hashes and wired20480 were verified before/after every
stage. These are accuracy regressions, not a new throughput or memory-pressure
qualification; the accepted warning-pressure and routing-latency limits stand.

The combined runner **exited 1**, not a pass: its isolated service registry still
owned ports8123/8124 when unchanged `test_cli.main` used the normal registry.
CLI startup correctly refused a server it did not own, before generating an
answer. The runner's finally block stopped its own servers and verified empty
state. This orchestration failure is retained in `regressions.log` and
`regressions/shutdown.json`. The unchanged CLI suite is rerun separately under
its own registry; completed earlier scores are not discarded or relabelled.

The separate unchanged CLI suite **exited 0 with all 18 checks passing**.
Its real remember/recall calls each produced an Auto/done permission row.
The installed CLI was also checked from `/tmp`: Auto read, Never recursive-delete
refusal, real terminal Confirm write, and project-scoped inspection all passed.
One final evidence-inspection helper initially used host `python3` and failed
with missing numpy; rerunning under `.venv/bin/python` passed, with no product
change. The helper failure is retained in `additional-failed-checks.json`.

**Final exit audit: PASS.** All 10 Phase 3 items are covered by the scoped
implementation and 14 adversarial control groups; no-drop live scores are as
listed above, all 18 CLI checks pass, and `./check.sh` **exits 0** with Python
3.12.13, MLX GPU, wired20480 and the verified03:00 backup. The final nuke dry-run
exits0 with **14,899 candidates**, all realpath-contained in code/, and the same
3 outward symlinks rejected. Destructive live-vault testing remains unperformed.
All read-only planning/research files match the preserved root commit. Runtime
servers owned by these checks were stopped cleanly.

Final evidence: `.session/phase3-20260921/final-verification.json`,
`regressions/{recall,abstention,quality,routing}.json`, `cli-final.json`,
`live-tool-audit.json`, `installed-cli.json`, `final-health.log`, and
`nuke-final.json`. The failed combined runner remains **exit1**; the final audit
independently verifies its completed stages plus the corrected standalone CLI
run. Frozen canonical recall SHA
`888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`
and bench SHA
`fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d`
are unchanged. Product Python sources were unchanged throughout measurement.

## MLX side probe — 2026-09-22 (measurement only)

Stage0 source audit: **Q1 supported at the installed mlx-lm0.31.3 Python API**. `LRUPromptCache(max_size=3,max_bytes=768*2**20)` provides bounded, multiple prefix entries; fetch/copy/trim reuse and safetensors save/load exist. The server saves system/user segment snapshots and completed generations. This does not establish llama.cpp-equivalent warm latency or checkpoint behavior. Its byte CLI flag only trims on batch admission; the sequential path needs an explicit byte-bounded cache integration. The unchanged benchmark adapter deliberately uses fresh full8-bit KV per request.

**Q2: no general JSON-schema/grammar decoder in the installed MLX-LM path.** The exact extension mechanism is pre-sampling `logits_processors` token masking. The existing adapter constrains only finite routing objects with a trie; tool arguments remain unconstrained. A migration would need a real compiler/token-mask integration for arbitrary tool schemas; GBNF is not directly accepted. Installed source/docs, line citations and hashes: `.session/mlx-probe-20260922/stage0.md` and `installed-source/`. Primary docs: [v0.31.3 caching](https://github.com/ml-explore/mlx-lm/blob/v0.31.3/README.md#long-prompts-and-generations), [cache implementation](https://github.com/ml-explore/mlx-lm/blob/v0.31.3/mlx_lm/models/cache.py#L1623-L1767), [sampling hooks](https://github.com/ml-explore/mlx-lm/blob/v0.31.3/README.md#sampling).

Stage0 clears Q1; Stage1 is authorized. No inference preceded this audit. Production configuration remains llama.cpp IQ3_S; no Phase4.1 work is being continued by this probe. Initial evidence setup hit a JSON integer-key comparison assertion, corrected before inference and preserved in `setup-failure.json`.

Stage1 completed with the unchanged `benchmark_mlx.py speed` command (exit0). Observed generation **33.084742 tok/s** versus IQ3_S26.637 (**+24.2%**); native prefill **81.823570 tok/s** for246 prompt tokens versus the supplied approximate87; model load **5.946821 s** versus supplied11.9s. One fresh-process128-token sample; decode excludes the first prefill-delivered token and includes final drain (127 timed tokens). Native pre-drain decode33.478909 is retained but not substituted. OS file cache was not flushed: load time is process-cold, not certified disk-cold. The existing adapter keeps its32768 admission ceiling, prefill step128 and fresh8-bit full KV; this short request does not certify32K. Both fixture/source hashes unchanged. Stage2 clears on competitive generation speed. Evidence: `.session/mlx-probe-20260922/stage1*.json`.

Stage2 continuous-load observation completed using unchanged benchmark_mlx.py soak600. Raw result (including the existing strict all-normal gate, not relabelled): `{"critical": 0, "device_wide_peak_gpu_allocated_bytes": 15820144640, "device_wide_peak_gpu_in_use_bytes": 15077687296, "duration_s": 606.2826194999798, "errors": [], "exit_code": 1, "legacy_all_normal_gate_passed": false, "mlx_allocator_peak_bytes": 14347518680, "normal": 119, "other": {}, "peak_sampled_rss_bytes": 4561453056, "process_lifetime_peak_rss_bytes": 9380331520, "warning": 1}`. Process RSS, device-wide GPU allocation/in-use and MLX allocator peaks are separate measures. This model-only probe never co-loaded Harrier or another llama.cpp server. Quality inference starts only after this soak process has exited.

Stage2 tool/answer measurements completed: coarse routing20/20, callable JSON20/20, tools18/20 first-pass and20/20 post-retry (two retries, t07 regex and t12 missing period; both failed first attempts retained), recall20/20 and abstention20/20. Recall and abstention replay the exact accepted real-Harrier retrieval payloads; generation is newly measured on MLX, while embedding/retrieval execution and its timing are not re-measured. This keeps the required llama.cpp/MLX runtime separation and identical fixed-path prompts. Test fixture files, prompts, scorer, cases and caps are unchanged. Full native outputs and input equality checks are under `.session/mlx-probe-20260922/stage2-*.json`. Actual302-leaf product routing remains in progress; its scores are not yet claimed.

Final decision: **branch 3 — MLX fork closed for this run.** Faster generation does not override the frozen routing regression. Product category20/20, **final lane19/20** versus IQ3's20/20. `r17` (difficult mathematical proof) emitted `formal_reasoning:001`, selecting `d01.s01.l02` (propositional/first-order logic proof construction), whose unchanged catalog pick produces Lane B; the frozen expected lane is C. The measurement-only transport constrained the exact existing finite catalog language through the adapter's existing token trie; no answer key entered its mask. `routing.decide`, catalog, prompts and scoring were unchanged. Quality process exit1 is retained; no retry/tuning/relabeling of this routing failure.

| Completed measurement | MLX DWQ4 | Existing llama.cpp IQ3_S comparison |
| --- | --- | --- |
| Generation, initial speed sample | 33.084742 tok/s | 26.637 tok/s |
| Prefill, initial 246-token prompt | 81.823570 tok/s | approximately87 tok/s, supplied baseline |
| Model load timer | 5.946821 s | 11.9 s cold server start, supplied; timer boundaries differ |
| Recall / separate abstention | 20/20 / 20/20 | 20/20 / 20/20 |
| Coarse routing / callable JSON | 20/20 / 20/20 | 20/20 / 20/20 |
| Tool exact first-pass / post-retry | 18/20 / 20/20 | 17/20 / 20/20 |
| Actual product category / final lane | 20/20 / **19/20 FAIL** | 20/20 / 20/20 |
| Soak normal / warning / critical | 119 / 1 / 0 (120 samples) | 25 / 96 / 0 (121 samples), historical shared-device observation |
| Strict all-normal soak gate | **FAIL, exit1** | IQ3 warning pressure already accepted |

The continuous-load observation lasted606.283s, with115 requests averaging31.087168tok/s (range29.403860–33.688498). Separate memory figures: sampled process-RSS peak4,561,453,056 bytes (4.56GB); whole-process lifetime peak RSS9,380,331,520 bytes (9.38GB); sampled device-wide GPU in-use peak15,077,687,296 bytes (15.08GB); device-wide GPU allocation peak15,820,144,640 bytes (15.82GB); MLX allocator peak14,347,518,680 bytes (14.35GB). Different counters/scopes are not interchangeable. Zero generation/monitor errors; the single warning sample is a real failure of the harness's strict all-normal criterion, preserved without treating the accepted IQ3 pressure history as a fresh control.

Q1 remains **supported through the bounded cache API**, with the stock sequential byte-budget integration gap documented above. Q2 remains **no installed general schema/grammar enforcement for tool arguments**; only a custom token-mask extension point and finite routing trie. No migration work follows this result. A future reconsideration would still need cache integration/peak accounting, measured warm routing under a768MiB/three-entry budget, complete tool-schema token masking and native frame handling, streaming/context/runtime-lifecycle integration, and all frozen gates again. None of that work was started here.

Final verification: both fixture SHAs match before/after (recall888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d; benchfdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d). All snapshotted production code/config/read-only plan hashes match. No model or package downloads, weight edits, routing/flag/prompt/fixture changes, or production configuration changes. `orbi.toml` remains llama.cpp IQ3_S. MLX measurement processes exited; no llama-server/MLX benchmark/server process or listener on8123/8124 remains. `./check.sh` exits0, wired20480, Python3.12.13, MLX GPU and03:00 backup verified. Phase4.1 stays paused with its pre-existing unfinished files preserved; Phase4C untouched.

Evidence: `.session/mlx-probe-20260922/final-summary.json`, `stage0.md`, installed-source snapshots/hashes, raw speed/soak/quality results and logs, `quality_probe.py` (measurement-only transport), and `check.log`. Stage0 evidence setup had one JSON integer-key assertion failure, corrected and retained in `setup-failure.json`; it occurred before inference and did not alter any benchmark score.

## Phase4.1 resumed — strict GBNF failure and correction (2026-09-23)

- 2026-09-23: First strict-GBNF full run FAILED: callable11/20, exact10/20, post-retry10/20. Evidence tools-after.json/log retained; harness exited0 despite failed scores (not a pass). Diagnostics isolated canonical property-order blocking: t05/t09 spent the256-token budget in whitespace. Changed compiler to unordered subset states, still requiring all required fields and forbidding duplicates/unknown keys. Both frozen diagnostic calls now exact, native stop eos;7,429 parser/native grammar checks pass. Full unchanged suite rerun starting.

Evidence: `.session/phase4.1-20260922/`; baseline17/20 first-pass,20/20 retry. Failed canonical-order raw output remains in inspect-truncation.log; corrected unordered diagnostic responses are in any-order-*.json. The diagnostic script reused two JSON filenames before they were copied; those original raw JSON envelopes were overwritten. The original raw text/log and complete failed tools-after.json score evidence remain. Corrected copies are explicitly renamed corrected-copy-*.json. No prompt, schema, fixture, sampling-cap, server flag or routing change.

- 2026-09-23: Corrected strict-GBNF frozen suite PASSED no-drop: callable20/20, first-pass17/20, post-retry20/20, coarse routing20/20; tools-after-v2.json/log, exit0. t07/t09/t12 remain string-content errors. Native unordered grammar fixes structural stalls, not semantic copying. New file/shell schemas now exposed through the same permissions.execute boundary; updated only obsolete Phase1 capability sentence in the product turn description, leaving SYSTEM_RULES and all benchmark/routing prompts unchanged. Nuke/Phase3 deterministic controls pass, including empty-system delete refusal and real PTY confirmation.

- 2026-09-23: File/shell executor checks16/16 and real CLI model calls for read_file/run_command pass. Image read scope is ImageIO pixel decode plus macOS Vision OCR, explicitly no scene interpretation; no projector/download. First F7 test failed because sandbox executable literal used the Homebrew symlink; realpath fixed the exact executable allowance. Initial image test used wrong glyph encoding; fixed fixture, exact OCR passes. Live nuke dry-run15,041 entries,0outside, includes three outward Python links themselves; temp-tree whole-root deletion already verified. Review caught shell poll completion race (fixed via conditional update+reread), binary capture/worker cleanup follow-ups, and WORD-only grammar triggering (added regex trigger for ordinary-token spellings). Integer generation now bounded100digits to avoid Python numeric parser mismatch. All failed evidence retained; final regression run pending.

- 2026-09-23: Final pre-regression deterministic gates passed:16file/shellitems, image OCR checks,7,432actual llama grammar checks, native-stream rejection tests, Phase3 controls, nuke adversaries. Shell review fixes now tested: binary streams preserved asbase64, stale polling cannot overwrite completion, timeout only marks a live process, SIGTERM cleans owned child, hard-killed worker child cleaned on inspection with PID/start identity. Real CLI file/shell smoke passed; offline editable reinstall exit0. Full unchanged recall/abstention/quality/routing/18CLI regression runner started with frozen-hash and wired20480 checks; no source edits during measurement.

### Phase4.1 implementation boundary

All model tool generation now renders the unchanged server Gemma template, then uses native `/completion` with per-request schema GBNF. There is no unconstrained fallback. Required fields, supported types, enums, integer bounds, array bounds and closed objects are enforced by the grammar; the parser independently rejects incomplete, duplicate, extra and trailing calls. Objects permit any property order. Unsupported schema keywords fail closed. Current compiler limits: at most10 object properties,100-digit integers,100-digit integer/fractional decimal parts with exponent magnitude99, and no native string delimiter embedded inside string content. String semantics remain the model's responsibility.

Both marker encodings activate grammar: WORD is converted to the dedicated token by [b10809 server schema](https://github.com/ggml-org/llama.cpp/blob/b10809/tools/server/server-schema.cpp); the added escaped PATTERN covers ordinary-token spellings and split token boundaries, following [sampling initialization](https://github.com/ggml-org/llama.cpp/blob/b10809/common/sampling.cpp) and [lazy grammar activation](https://github.com/ggml-org/llama.cpp/blob/b10809/src/llama-grammar.cpp). Native token/end markers are preserved, thinking frames are separated, and a length-stopped tool call never reaches execution.

The Phase3 executor owns all authorization. File write/edit reuse its exact-diff approval and path guards. Readers supply numbered UTF-8, bounded byte ranges/base64, non-following glob traversal, regex/type-filtered ripgrep, PDF text and local ImageIO/Vision OCR. Image content beyond OCR is explicitly unavailable; this is not a multimodal scene-understanding claim. PDFs with only scanned pixels may have no extractable text.

Shell is deliberately a closed read-only command set: `echo`, `printf`, `true`, `false`, `sleep`, `ls`, `cat`, `wc`, plus persistent `pwd`/`cd`. Existing guarded `git status` remains available. There is no shell evaluation, interpreter or arbitrary build execution. The native macOS sandbox denies writes, network and child executables; mutations stay on the approved typed path. Foreground and background results retain real exit codes, bounded streams and timeout outcomes; undecodable streams retain base64 bytes. A background worker survives its caller, cleans children on SIGTERM, and records its child's process identity so inspection can clean up after a hard-killed worker. Hard-kill cleanup occurs on inspection, not via an always-running supervisor.

Nuke uses lstat for each entry's own identity, lexical own-location containment, realpath for directories and no-follow directory descriptors. It unlinks outward/dangling/looping links themselves and does not visit their targets. Only throwaway trees were actually deleted, including their roots. Live use was dry-run only.

Deferred unchanged: slices4.2–4.5, web fetcher and Granite Guardian, all computer mode4C, and the catalog's four inert computer leaves. Computer input/screen capture remains a deliberate placeholder Never guard. MLX remains closed; r17's X no-match escape and routing source/catalog are unchanged. No models, weights, production configuration, frozen server flags, benchmark prompts or frozen fixtures were changed.

Auxiliary evidence fetch initially failed with the host Python3.14 certificate-store error; system curl fetched the same pinned sources with TLS verification enabled. Source hashes and the failed fetch record are in upstream/. This did not affect inference or scoring.

- Full unchanged regression runner exited0: recall20,abstention20,coarse routing20,callable20,tools17first/20retry,product category20/final lane20 includingr17 X->C,18CLIchecks. Source snapshots fixed throughout. Subsequent PDF-wrapper audit reproduced a boundary bug: a UTF8 byte cap could make the shared capture returnbase64, which the PDF wrapper omitted. Corrected only that result pass-through and added a focused regression; no model/schema/prompt/routing change. Re-running the16file/shell checks for this isolated change.

### Phase4.1 exit audit — 2026-09-23

| Gate | Result |
|---|---|
| Files / shell |10/10 and6/6; image scope is decode + OCR|
| Schema GBNF |7,432 real pinned-engine acceptance checks; stream failure controls pass; effective schema grammar and both trigger forms verified on23 native generations|
| Frozen tool first-pass, before → after |17/20 →17/20|
| Callable / post-retry tools |20/20 /20/20;3retries|
| Recall / abstention |20/20 /20/20; recall request bodies identical to accepted IQ3 baseline|
| Routing category / final lane |20/20 /20/20; r17 remains unmapped:formal_reasoning →C|
| CLI/control |18/18 unchanged checks|
| Nuke dry-run |15,121 entries;0outside code/;three outward Python links included as entries to unlink|
| Nuke deletion |Complete removal in throwaway trees only; outside targets survive|
| Health / shutdown |check.sh exit0; wired20480;03:00 backup registered;owned runtime records empty and ports8123/8124 closed|

Primary evidence: `.session/phase4.1-20260922/final-audit.json`, `regressions/summary.json`, `grammar-attestation.json`, `nuke-dry-run-final.json`, `files-shell-pdf-fixed.log`, `shell-lifecycle-first.log` and `check-final.log`. Final PDF wrapper correction only retains the existing base64 capture on a split UTF8 boundary; its focused reproducer first failed, then all16file/shell controls passed. It changes no model schema or inference path.

Failures retained: original canonical-order GBNF run11/20callable and10/20exact/post-retry; helper JSON round-trip and missing-slot-field inspections; Homebrew executable symlink sandbox rejection; image fixture glyph encoding; PDF byte-boundary loss; optional source-fetch TLS error; and the audit's initial comparison against the older pre-pause plan snapshot. Correct resume hashes and root7d1643b show the read-only vault unchanged. Two diagnostic raw JSON envelopes were accidentally overwritten; their original raw stdout and the full failed-suite result remain, and corrected copies are labelled honestly.

No final gate remains failed within the declared image/closed-command scope. t07/t09/t12 still fail first-pass string content, as before; grammar does not repair them. Existing failures are not relabelled as passes. Slices4.2–4.5, guard model and Phase4C remain deferred; the computer-use placeholder guard stays enforced. MLX remains closed, measurements preserved, IQ3_S retained. Both frozen fixture SHAs, routing/catalog/config and read-only planning files match the resume baseline.


## Phase 4.2 — Git and instruction skills (2026-09-23–24, validated)

Scope: Group 7 six Git items and Group 8 five instruction-skill items. Existing executor and strict native GBNF are reused. Production routing, prompts, model, flags, catalog and frozen fixtures remain unchanged. MLX remains closed; t07/t09/t12 are accepted retry cases, not optimization targets. Evidence: `.session/phase4.2-20260923/`.

- `phase3-first.log`: existing permission controls pass unchanged.
- `controls-first.log`: **failed** at the first real temporary bare-repository push because Git on this case-insensitive macOS adds `core.ignorecase` and `core.precomposeunicode`; the remote config allow-list omitted those harmless fields. Added them; no transport or permission bypass.
- `controls-second.log`: all 11 checklist controls pass, plus 35 native llama.cpp grammar checks for the seven new model tools. PR creation uses a controlled API fixture, not a live posted PR. Real branch/switch/commit/push tests run only in throwaway repositories inside the allowed root, with independent remote SHA checks and a rejected non-fast-forward. Final review and unchanged model regressions are pending.

Git mutation intent comes from direct `orbi tool` invocation or one-prompt `--git commit|push|pr`, outside model arguments. A model commit must first inspect the real staged diff; its SHA binds the proposed message to that review. All mutations still require terminal confirmation. Only GitHub HTTPS and in-root bare origins are implemented; other transports and executable repository config are rejected. PR creation uses `gh api` POST, which cannot implicitly push. Instruction packs declare required tools, not permission grants; project `.orbi/skills/NAME/SKILL.md` overrides `code/skills/NAME/SKILL.md`.

- Expanded local-remote test **failed** (controls-third.log): receive-pack executed the throwaway remote hook because client -c core.hooksPath is not inherited by that server process. Added a fail-closed local-remote hook guard before transport, plus a negative assertion that the marker is never created. Only the temporary test tree was affected; no live repo or runtime.

- `controls-fourth.log` and `test_phase42-final.log`: all11 controls pass after the local-hook fix;35 new-tool native grammar checks. Existing Phase3 controls,16 file/shell controls,7,432 compiler acceptance checks, native stream validation and nuke adversaries pass unchanged.
- `smoke/results.json`: live Gemma generated grammar-constrained git_read and load_skill calls through the real executor; explicit requested-skill injection also worked. Each Auto decision and result was checked. Runtimes stopped and both frozen fixture hashes verified afterward. The CLI-injected skill case voluntarily reloaded the same pack before reading Git status; this is retained in the audit.
- Existing PyYAML6.0.3 is now an explicit package dependency; offline editable reinstall exited0. No download. Full no-drop regression run is in progress with fixed production sources and wired20480.

- **First full regression failed**: recall20/20, abstention20/20, callable20/20, tools17/20first and20/20retry, CLI18/18, but product routing harness19/20. r05 classified correctly as memory_lookup/A, then the changed all-tools context elicited run_command("ls -R"); the existing executor correctly refused its unsupported option, and the turn failed. This remains a failed gate, not a routing pass. Evidence: regressions/routing.json and routing-ce782ebf0e034908aec297efc5a0b68d/routing.sqlite3. No shell policy or prompt tuning. Corrected tool exposure: retain exact Phase4.1 BASE_TOOLS for default requests; explicit --git tools|commit|push|pr or --skill selects the extended grammar-constrained tool set. A fresh complete regression is required on this correction.

- Scoped-tool correction initially failed a frozen Phase3 callback signature (phase3-scoped-tools.log): an unnecessary tools keyword was passed on the default path. Preserved the original default call signature; phase3-scoped-tools-corrected.log now exits0 without changing the frozen test. Added a regression check that default requests never include Git schemas, while explicit task options use the extended grammar.

- Resumed Phase4.2: live installed CLI commit passed through the real model, GBNF, staged-diff hash review and terminal preview. Generated message: "Increase request_timeout_seconds from 30 to 45 in settings.json"; resulting temporary commit and file content independently verified. Evidence live-commit/result.json; runtimes stopped, frozen hashes held. Independent security review then identified untested local-remote indirections (commondir/nested .git/alternate stores, symbolic feature refs targeting main), hidden assume-unchanged/skip-worktree edits, and inconsistent gitlink diff visibility. Added pre-transport/pre-status refusals and throwaway adversarial checks. Exact staged/tree diffs now include gitlink summaries; worktree submodule diff/switch is refused before entering a submodule. No live-vault deletion or outside-repo mutation. Final full regression is pending on these fixes.

- Final review confirmation: remote indirection/symbolic-ref guards and hidden-index/gitlink guard ordering verified read-only by the reviewer. Eight deterministic scripts exit0 on final source (deterministic-release.json): Phase3, all11 Phase4.2 controls, all16 Phase4.1 controls, native grammar/runtime, tool validation, routing persistence and nuke adversaries. Corrected opt-in live smoke is running; no further production edits during measurement.

### Final Phase4.2 result

**11/11 Git/skill controls pass.** `deterministic-release.json` records eight passing deterministic scripts, including the existing16 file/shell items, Phase3 hard test, native runtime validation,7,432 existing grammar checks plus35 new-tool grammar checks, routing persistence and nuke adversaries. `smoke-corrected/results.json` records actual model Git/skill execution; `live-commit/result.json` records a real installed-CLI/model commit after exact-diff terminal approval in a throwaway repository.

The final unchanged regression (`regressions-corrected/summary.json`) exits0: **recall20/20, abstention20/20, category20/20, final lane20/20, callable20/20, tools17/20 first-pass and20/20 post-retry, CLI18/18**. Complete recall requests match the accepted fixed-path IQ3 baseline. r05 now returns UNKNOWN successfully; r17 emits `formal_reasoning:X`, keeps no matched leaf, and falls back to Lane C. t07/t09/t12 remain first-pass failures corrected by the unchanged retry path. No prompts, routing, catalog, quant, server flags or frozen fixtures changed.

**Tool exposure is explicit:** ordinary requests retain the original12-tool surface. `--git tools|commit|push|pr` or `--skill NAME` selects the19-tool surface, still using the same native GBNF and permission executor. Universal19-tool exposure failed r05 and is not certified; that failed full run remains in `regressions/`. The corrected smoke checks cover explicit extended-tool requests, including --skill without a Git option.

`check-final.log`: check.sh exit0, Python3.12.13, wired20480,03:00 backup verified. Both runtime ports closed; final source/fixture hashes match the measured run. A final vault-start hash check failed because separate root commits `fa97432`/`4ecbc1e` introduced plan v28/model-list updates during this task. Those committed changes are preserved, not attributed to this slice; the read-only vault matches current root HEAD (`final-audit.json`).

PR permission/payload/response handling is tested with a controlled API fixture; no live PR was posted. GitHub authentication and repository push permission were separately verified read-only. Git support currently requires already-staged commits and local author identity, clean regular-file switches, and either GitHub HTTPS or a canonical in-root bare remote without active hooks, redirected stores or symbolic branch refs. Exact staged/tree gitlink summaries are supported; submodule worktree diff/switch is refused before entering submodule configuration.

Deferred unchanged:4.3 hooks,4.4 subagents/batching,4.5 web/cloud/guard model, MCP work and all4C computer mode. Computer input/screen-capture placeholder remains enforced. MLX stays closed. No model download or skill_catalog.py edit.

Final live nuke dry-run: 15452 entries, **0 outside code/**, including the three outward Python links themselves. Real deletion was tested only on throwaway trees.

## Phase 4.3 hooks — 2026-09-24 through 2026-09-26

Evidence: `.session/phase4.3-20260924/`. Phase4.2 PR #1 was merged by non-force
fast-forward; independent `git ls-remote` confirms main at
`c45a0921804497c400ec5d7d524e6e95a0368f66`. Work continues on `phase4.3-hooks`.

Hooks require explicit `--hooks` configuration and add no model tools. Selected
shell scripts are snapshotted, then run as child decisions through the existing
executor and sandbox. Only shell control/data builtins are available; external
commands, forks, writes, network and GUI IPC remain denied. A mandatory selected
Never hook is a second veto; removing hooks leaves the original code checks.
Output stays escaped, untrusted tool data, never parsed as actions or approval.

Pre-hook crash/timeout/nonzero exit prevents the action. A post-hook runs after
execution: its failure cannot undo the action; the completed result is retained
in the audit, further calls are blocked, and the task fails. This is an explicit
lifecycle limit, not a claim of rollback. No live injection-resistance score is
claimed from the data-boundary tests.

Before checks: wired limit20480; recall fixture SHA
`888ef490698581f985dc8e2486b321d32bc1bc5bc231dc93614c7a309889090d`, benchmark SHA
`fdcf669576169038916ba421e097ba9fee3854aae01873c5b6e6f25287e3e86d` verified.
Default schemas, model, prompts, routing, catalog and frozen flags unchanged.
Final deterministic and unchanged live results follow below. Slices4.4/4.5, MCP and4C
remain deferred; computer-use placeholder stays; MLX fork remains closed.

Failures retained: `controls-first.log` failed the intended crash assertion
because the test selected the wrong Bash argv slot and actually exercised a
timeout. The test now locates `-c` explicitly. Independent review also found
the new hook JSON envelope hid nonzero command status at the CLI boundary;
exit propagation was corrected and covered by a CLI assertion. Neither is
counted as a pass. The unchanged Phase3 controls already exit0.

Corrected hook controls passed in `controls-second.log` through
`controls-fourth.log`. Review additionally found post-hook failure could overwrite
a background worker's status (and cancellation had the same edge). Action status
is now preserved for every exception after execution; the child hook independently
records failure/cancellation. Tests cover real background completion and retained
hook refusal. Final deterministic and live gates are recorded below.

Final deterministic result: all11 scripts exit0 (`deterministic-release.json`),
including all5 hook items, prior Phase3/4.1/4.2 controls, native grammar/runtime,
tool validation, routing persistence, nuke, shell lifecycle and image controls.
The real installed CLI `--hooks` smoke also passes (`smoke/results.json`): actual
model/GBNF read_file followed by three successful shell-hook child decisions
(Never, pre, post), with feedback persisted and supplied to the model. This smoke
certifies dispatch and feedback, not an extra quality score. Runtimes stopped and
fixture hashes held before the full unchanged regressions began.

The first live regression (`regressions/`, exit130) was deliberately interrupted
for an audit-edge fix before source edits: recall20/20 and abstention20/20 had
passed, but quality/product routing/CLI were unfinished. It is **not** a completed
gate. Runtimes stopped in the runner's finally block; hashes verified. The64KiB
event check originally ran before child-decision insertion, leaving oversized
post-hook input without its own failed hook row. It now runs inside that logged
decision; a large-result check verifies failed child plus successful parent.
Final evidence uses `smoke-final/` and `regressions-final/` without overwriting
the initial run. A PID lookup first returned no match because macOS reports the
Python executable with a capital P; no process was signalled until its exact
command and PID were verified.

Resumed2026-09-26: `smoke-final/` had passed and stopped cleanly. The wired limit
had reset to0, so inference was held until the user restored20480; verified
before launching `regressions-final/`. Concurrent vault plan/name/logo changes
are separate work and remain outside this slice. Production source/fixtures
are frozen throughout the final runner.

### Final result — all exit gates pass

`regressions-final/summary.json` reports the unchanged suites:

| Gate | Result |
|---|---:|
| Recall / abstention | 20/20 each |
| Product category / final lane | 20/20 each |
| Callable JSON | 20/20 |
| Exact tools, first-pass / post-retry | 17/20 / 20/20 |
| CLI/control checks | 18/18 |

Only the accepted t07/t09/t12 first-pass misses remain, each recovered by one
retry. No attempt was made to tune them. r05 passes on the unchanged default
surface; r17 emits `formal_reasoning:X`, leaf null, and preserves Lane C fallback.
Recall request bodies match the accepted IQ3 baseline exactly. All fixture and
source hashes held across measurement.

All5 hook items pass. Eleven deterministic scripts passed; after the final event
cap audit fix, the affected hook suite passed again (`controls-cap-fix.log`).
The final installed-CLI smoke passed (`smoke-final/`); all model calls still use
the existing GBNF layer with unchanged12/19 default/opt-in schemas. No hook tool
is exposed to the model. Hook-free Phase3 Never enforcement remains intact.

Health failures retained: `check-final.log` and `check-corrected.log` exit1 due
to missing/mismatched backup registration after login. The installed CLI registered
the Python3.12 alias, while the existing health check requires `.venv/bin/python`.
After verifying ownership and that the job was idle, only Orbi's backup job was
reloaded using `.venv/bin/python orbi.py --schedule-backups`. `check-restored.log`
exits0 and verifies the03:00 job, Python3.12.13 and wired20480. No health-check,
production source or frozen runtime changes were needed for this restoration.

Final source snapshot verified unchanged; both runtime ports are closed and the
runner's owned service state is empty. Interrupted/failed evidence is retained,
not counted as a pass. Scope remains hooks only:4.4,4.5, MCP, computer mode,
rename/licence implementation and cloud setup are deferred; MLX stays closed.

## Kildall rename slice — 2026-09-26, in progress

Phase4.3 was integrated through PR#2 by an ordinary non-force fast-forward;
independent `git ls-remote` verified main at
`e257865bb57c189fbf40e8b8ec1c679e31a54c53`. The working branch is
`rename-kildall`. GitHub is now `MinhDuc2612/Kildall`; origin uses the new
URL, and the old web URL redirects to it with HTTP200.

The live filesystem differs from the rename brief: the vault already resides at
`/Users/minhduc/Kildall`, with `Klogo.png`; `/Users/minhduc/Orbi` and `Plogo.png`
are absent. User clarification is pending. The hardcoded permission root remains
`~/Orbi/code`, as required. No folder move, logo copy, live data cutover, runtime
reinstallation or launchd replacement has been performed. The old backup job is
registered but points at the absent original path; that is not a healthy schedule.

Completed independent work: primary module/setup/config names, package and both
console entry declarations, MIT license, display strings and documentation, plus
mechanical test imports. The `orbi` Python alias shares module state with `kildall`.
Direct-script execution now registers the same module identity. Backup scheduling
normalizes a sibling `python` alias only when it resolves to the exact interpreter,
matching the existing health-check requirement. SQLite tables, model prompts,
tool schemas, routing behavior, catalog, grammar and server flags are unchanged.
The frozen fixture bytes and canonical recall fixture remain authoritative.

Six independent control scripts pass: exact-tool validation, native GBNF,
completion adapter, temporary-tree nuke, synthetic memory and health-check
failure paths. This does not claim live model, production dry-run or health gates.
The first new rename compatibility test failed because its temporary-directory
expectation used `/var` while settings correctly canonicalized to `/private/var`;
the failed log is retained as `test_rename.log`. The test expectation was corrected
to use the real path; its result is recorded separately.

An exclusive-lock SQLite backup of live `orbi.db` was copied to evidence and
verified by `integrity_check`, schema hash, all-table row counts and row hashes.
It has nine permission records and no memory/session/message/task records. All14
historical SQLite backups pass integrity checks. No live record or original backup
was deleted or renamed. Evidence: `.session/rename-kildall-20260926/`, including
`memory-audit.json`, `independent-controls.json`, `static-invariants.json`,
`github-rename.json` and `integration.json`.

Pending: resolve fixed-root/source-logo mismatch; verified live database/backup
cutover; installed commands; new launchd registration before removal of the old
job; production nuke dry-run; full unchanged no-drop regressions; `check.sh`;
rename commit, push, independent SHA verification, PR and fast-forward merge.
No Phase4.4 work started.

Corrected rename compatibility controls exit0 (`test_rename-corrected.log`):
shared alias/direct-script state, legacy configuration fallback, new-variable
precedence and canonical backup interpreter. Both source-script help commands
exit0 from outside the checkout. Installed-entrypoint verification remains pending.

User clarification: the vault move to `~/Kildall` and logo rename to `Klogo.png`
were deliberate. The sole production allow-list is now `~/Kildall/code`. Current
commands/configuration/README use that root; historical raw evidence remains
unchanged. The write-tool description changes only its displayed allow-root path.
Recall request and server-command comparisons will normalize only the old/new
vault path components; prompts, fixtures, settings and score thresholds stay fixed.

### Rename migration and controls — 2026-09-27

The path question is resolved: retain `~/Kildall` and use `Klogo.png`. The logo
copy at `assets/kildall-logo.png` matches the source SHA256; both root logos are
unchanged. LICENSE and package metadata declare MIT, copyright2026 Nguyen Hoang
Minh Duc. `kildall` and the one-release `orbi` command/module alias share state,
configuration and the migrated database. `KILDALL_CONFIG` takes priority over
the supported legacy variable; no access was made to `~/.config/orbi/`.

Recreated `.venv` with Python3.12.13 at its new absolute location, preserving the
old environment in evidence. The wheel cache was incomplete; only missing locked
packages and three compatible cp312 replacements were fetched. The first offline
resolution failed because cached MarkupSafe/PyYAML/sentencepiece wheels targeted
cp314; the failed log is retained. The corrected local wheelhouse resolved and
installed the unchanged34 requirements plus setuptools80.9.0 offline. `pip check`
passes. Both installed commands and the shared import identity work from outside
the checkout. No weights, runtime selection, model flags or inference settings
changed; fetching existing locked MLX libraries did not reopen the closed MLX fork.

The migration copies live `orbi.db` to `kildall.db`, copies14 historical SQLite
snapshots into the new backup namespace, and renders14 mirrors from those verified
new snapshots. Original databases and mirrors remain available for recovery.
Exclusive activity locks and a SQLite write reservation cover the live copy; no
unfinished tasks or shell jobs existed. Copies pass integrity, schema, counts and
all-row hash comparisons, with only explicit project/cwd fields normalized to
the new root. Nine live permission project paths changed; no record was dropped.
Historical command/decision payloads remain unchanged. Synthetic nonempty memory,
vector, FTS and session controls also pass. No live `.orbi/skills` directories were
found requiring migration. See `migration.json` and `skills-migration-inventory.json`.

Registered and verified `local.kildall.backup` with new absolute paths and03:00
schedule; `check-new-backup.log` exits0. Only afterward removed the owned legacy
registration, verified its absence, and retained its old plist as evidence. The
first retirement assertion failed because the inactive old job was `spawn scheduled`
rather than `not running`; after checking active count0, noPID and its absent
original executable, the corrected retirement succeeded. This did not change or
weaken the production health check.

All14 deterministic scripts pass (`deterministic-final.json`), covering Phase3,
all16 files/shell items, all11 Git/skills items, all5 hook items, GBNF/completion,
exact arguments, routing persistence, nuke adversaries, shell lifecycle, image
reader, memory, health failures and rename compatibility. Nuke's live dry-run
reports29320 entries, zero outside the sole `~/Kildall/code` root, zero rejections,
and all three outward Python links as entries. Destructive checks used only
throwaway trees. Full live no-drop regression results follow when complete.

### Final rename exit gates — 2026-09-27

| Gate | Before | After |
|---|---:|---:|
| Recall |20/20|20/20|
| Abstention |20/20|20/20|
| Product category |20/20|20/20|
| Final lane |20/20|20/20|
| Callable JSON |20/20|20/20|
| Exact tools, first pass |17/20|17/20|
| Exact tools, post-retry |20/20|20/20|
| CLI controls |18/18|18/18|
| Hook items |5/5|5/5|

All Phase3/4.1/4.2 controls pass. The three first-pass misses remain t07/t09/t12,
with the same three successful retries; no attempts were made to tune them.
`r17` emits `formal_reasoning:X`, with no leaf and LaneC fallback.

All20 complete recall requests match the accepted IQ3 baseline after replacing
only `/Users/minhduc/Orbi/` with `/Users/minhduc/Kildall/`; raw requests are
retained and explicitly recorded as different. Server commands also match after
that path-only normalization. Fixture file bytes, canonical recall SHA888ef490…
and bench SHAfdcf6695… remain unchanged before/after every stage. Source hashes
remained frozen throughout inference. See `regressions/summary.json`,
`recall-request-comparison.json`, `runtime-comparison.json`, and
`final-semantic-audit.json`.

Both installed commands work, including inspecting a migrated historical audit
record through `orbi`. Final `check.sh` exits0 with Python3.12.13, wired20480,
MLX GPU availability and the new03:00 backup job verified. The owned runtimes are
stopped, service-state files are empty, and both ports8123/8124 are closed.
Final nuke dry-run: 29413 entries, zero outside `~/Kildall/code`,
zero rejections; no live destructive test. See `nuke-final.json` and
`check-final-verified.log`.

The retained rename-test, incompatible-wheel resolution and old-job state-check
failures are documented above; all corrected controls and final gates pass.
Original live DB,14 snapshots,14 mirrors and the old environment remain available
for recovery. The protected planning files, Researchhub, source logos and API-key
configuration were untouched. Deferred: Phase4.4/4.5, MCP and all of4C; the computer
placeholder guard remains enforced and the MLX migration fork stays closed.

## Phase 4.4 — baseline, slot sizing and failed second-process probe (2026-09-27)

Evidence: `.session/phase4.4-20260927/`. Pinned b10809 source audit verifies total context splits across explicit slots, 768MiB is a global saved-prefix cache, and three checkpoints are per live slot. Original single-slot settings/prompts/12-tool surface held for 100 measured inference requests after four warmups: p50 **5.986s**, p99 **6.114s** (nearest-rank), 32 generated tokens each; 0-child candidate limit **6.726s**. This includes rendering/HTTP/SSE, excludes CLI startup and memory I/O. Frozen fixture hashes and wired20480 held.

One versus two slots, each4096 context: warmed process RSS grew by **533,315,584 bytes**, device GPU allocated by **234,979,328 bytes**. Both slots reused1812–1813 prefix tokens (one prompt token evaluated) in repeat requests. Sizing uses measured free+inactive+speculative pages, minus2GiB reserve, divided by observed incremental RSS; this selects **2 total slots**. This is a measured admission estimate, subject to the latency and600s soak gates, not a certified memory peak.

**FAILED:** the actual second IQ3 model process reached peak RSS **11,635,621,888 bytes**, but concurrent generation caused Metal `kIOGPUCommandBufferCallbackErrorOutOfMemory` and HTTP500 in both servers. Both were stopped cleanly; raw failure/logs retained. macOS pressure sampled25normal/0warning/0critical despite GPU allocation failure: pressure alone is insufficient. Separate-process cap is **0**, both by the measured free-RAM formula and by failed execution certification. RSS includes shared mmap pages; summed process RSS is not physical incremental consumption. No5GB assumption. Final quality/soak/delivery gates remain pending.

Initial Phase4.4 deterministic controls: existing Phase3/4.1/4.2/hooks/transport/shell lifecycle all pass. `controls-phase44-a.log` **failed** because the new test incorrectly expected `before=null` for a new-file diff; existing executor correctly returns empty text. Corrected assertion only; `controls-phase44-b.log` passes own-context overlap, parent terminal approval, inherited tools/project memory, prompt-free Never/recursion, cap0/refusals, cwd/job isolation, real HTTP cancellation and crash cleanup. These are deterministic controls, not live quality or throughput certification.

**FAILED before load:** `child-soak-a` admitted no children: measured free+inactive+speculative1,919,156,224B, warning pressure, below the initial2GiB shared-admission threshold. The guard incorrectly reused the new-process reserve after resident KV was allocated. Shared admission now requires available RAM at least `active children × measured slot RSS increment` (1,066,631,168B for two), plus no critical pressure and the measured two-slot cap. Separate-process admission retains2GiB reserve and cap0. This is an explicit admission-policy correction, not a passing soak; raw refusal, one pressure sample and failed log retained.

**Pre-existing synthetic test failure reproduced on main70eb4e8:** `test_benchmark.py` still mocked only the old HTTP completion entry point, so Phase4.1 native tool requests escaped its mock and the synthetic20/20 assertion failed. Current-branch failure and isolated-main reproduction retained (`controls-release/`, `test-benchmark-main.log`). A preview updating only the native-tool mock seam passes every unchanged assertion/fixture; production evaluator and frozen suites are untouched. Applying the test-only seam repair after the source-frozen soak finishes.

First complete real-child soak (`child-soak-b`): **600.046s observation**,121samples = **103normal/18warning/0critical**, versus historical25/96/0. Load611.574s,25batches/50children,3189generated tokens. Peak Lane A RSS13,278,478,336B; device GPU in-use14,562,492,416B and allocated15,399,075,840B, reported separately. Child inference p5024.738s/p9925.677s with actual bounded retrieval/context and64-token reply cap; total5.214tok/s including prefill and memory/tool overhead. This differs from the fixed32-token HTTP latency protocol and is not a generation-only rate. Live parent delegation also passed: native GBNF emitted spawn_agents, two processing server slots overlapped, and CHILD_ALPHA/CHILD_BETA returned to the parent.

Final review added server-idle draining before a cancelled slot can be reused, and forwarded automatic memory-hook outputs to the parent as data. Both have deterministic controls. The stale synthetic evaluator mock seam is now repaired; all assertions and frozen fixtures are unchanged. A fresh source-frozen600s soak and final latency/scaling/regression chain will verify this final revision; prior results remain intact.

Final deterministic controls (`controls-final/results.json`): **15/15 scripts exit0**. Coverage includes prior Phase3/4.1/4.2 and all5 hook items; own child contexts and results; parent-terminal confirmation; inherited tools/Git intent/project-only memory writes; prompt-free recursion and Never refusals; linked action records; independent child cwd/jobs; real SIGINT, blocked HTTP cancellation and crash cleanup; strict grammar and idle slot handoff. Separate-server launch/cleanup is tested with simulated admission only; successful dual-model inference is **not** claimed. Actual cap0 follows the failed hardware probe.

### Pre-review source-frozen child soak

`child-soak-final/`: **600.049s** observation,121samples = **121normal/0warning/0critical**; historical single-slot reference25/96/0.52real child contexts in26batches completed over623.632s load, using actual retrieval, memory writes and the shared executor. Peak Lane A process RSS **13,474,529,280B**; device-wide GPU in-use **14,160,969,728B**, allocated **14,891,909,120B**. The device figures include other GPU allocations and are separate from process RSS. Pressure observations are machine-state dependent, not an isolated physical-memory comparison.

With64-token reply caps and growing bounded memory context, child inference p50 **24.436s**, p99 **25.129s**,3316generated tokens and **5.317tok/s** across total load wall time. This is the real-child soak workload, distinct from the fixed32-token latency/scaling protocol. All source and frozen fixture hashes held; owned runtimes stopped cleanly.

**FAILED final parent exact-once smoke (`live-parent-final/`):** the parent first emitted child prompts `CHILD_ALPHA` and `CHILD_BETA`, omitting the requested `Reply exactly`. Both children returned UNKNOWN. The parent then sent corrected prompt strings in a second batch and returned both expected answers. The smoke assertion requiring exactly2children failed:4children completed across2batches. This is an opt-in delegation argument-content/instruction-following failure; GBNF guaranteed valid structure, not those strings or the requested single invocation. It remains a failed run. All4children had linked records, completed, and at most2processing slots were observed; no safety/cap failure. Earlier `live-parent-a` passed, and the final52-child soak passed, but neither erases this failure. No prompts, schemas, fixtures or production code were changed to chase it. Frozen default-tool quality gates follow independently.

### Pre-review interactive inference latency

Same100payloads,32reply tokens and4warmups, with zero children. Nearest-rank percentiles; rendering, HTTP and SSE included, CLI startup and memory I/O excluded.

| Configuration | p50 (s) | p99 (s) | Total tokens / wall (s) | Total tok/s |
|---|---:|---:|---:|---:|
| Single slot,4096 total context |5.986|6.114|3200 /600.276|5.331|
| Two slots,8192 total context, zero children |5.957|6.132|3200 /596.717|5.363|

Final p99 increased **0.28%**, below the10% limit (**6.726s**). `candidate-zero-final/summary.json` passes. The earlier candidate-a result,6.339s/+3.68%, also passed and remains recorded; the pre-review source revision is the result above; the corrected-source repeat follows below. These end-to-end inference rates are not Lane A generation-only tok/s.

### Regression harness incompatibility — 2026-09-28

**FAILED `regressions/`: recall0/20, exit1.** Every recall row raised `Cannot verify the completed single-slot recall request`: frozen `test_recall.py` requires `len(/slots)==1` after generation, whereas this phase deliberately runs2slots. It rejects before assigning/scoring the answer. Diagnostic inspection finds20/20raw responses match the unchanged aliases, but the recorded run remains0/20 and failed. No frozen file or score was rewritten. The queued final verification timed out because the chain was unsuccessful.

Other unchanged gates in that same run passed: abstention20/20, product category/lane20/20, callable20/20, tools17/20first and20/20post-retry, CLI18/18. t07/t09/t12 remain the three first-pass misses; r17 retains its no-match escape. Both runtimes stopped. A separate unchanged one-slot frozen run and explicitly documented per-slot verifier will distinguish fixture compatibility from production two-slot recall quality.

### Shared inference scaling

Same100fixed32-token requests per point; one warmup per worker excluded. One resident process, separate pinned contexts. These per-request measurements include template/HTTP/prefill/stream but exclude memory/tool work; the real-child soak separately includes that work. **N=2**, so2andN are the same measured point, not separate experiments.

| Concurrent contexts | p50 (s) | p99 (s) | Total tok/s |
|---|---:|---:|---:|
|1|6.036|6.295|5.274|
|2 = N|11.644|12.306|5.476|

Aggregate throughput gains **3.82%**; per-request tail latency rises substantially under concurrency. This is interleaving with a measured two-slot ceiling, not a large throughput win. Source `.session/phase4.4-20260927/scaling-a/summary-*.json`. Product routing on the unchanged20cases averages **6.720s**, versus the historical5.06s; category/lane20/20 and r17`formal_reasoning:X` hold.

Routing cache detail:7cold classifications average17.761s;13warm classifications average0.776s and reuse3866tokens. The server log records global768MiB cache evictions while an idle second slot retains a prompt. Thus both slots can reuse prefixes, but the shared budget does not preserve every router snapshot across intervening answer requests. The measured6.720s product mean is a regression from5.06s and is reported as a cost, not hidden by the short-request p99 result. No cache/flag/prompt/routing tuning was attempted.

### Final review corrections — 2026-09-28

**FAILED new capability regression:** the model-dispatch helper could grant the internal transcript-write capability solely from action name `_agent_memory`. Strict GBNF excluded that name, but the executor boundary must remain independently closed. `review-capability-red.log` reproduces the failure. The helper now grants that capability only for trusted `automatic=True` calls; direct model-path invocation is refused without any memory write.

Review also found that template/tokenization preflights used ordinary HTTP sockets before entering cancellable generation. A stalled preflight could delay Ctrl-C cleanup until its30s timeout. Child-only cancellation now owns all template/tokenization/completion requests. Real stalled HTTP controls at all3preflight stages pass; ordinary requests retain their existing transport and payloads. No model/prompt/schema/flag changes. These corrections supersede the earlier source snapshot; fresh final controls/soak/regressions follow.

**FAILED normal-background outcome regression (`review-background-red.log`):** a child that launched a background job and returned could be reported successful even though batch cleanup cancelled that job. Cleanup now returns the cancelled-job outcomes to the parent and marks that child as failed; done is saved only after cleanup. Interrupted unfinished children remain cancelled. The corrected test passes; final read-only review confirms all3findings fixed. Fresh final controls and model/soak checks use `release-post-review.json`. Earlier timing runs remain evidence for unchanged model/flags/payloads; their exact source snapshots are retained rather than rewritten.

### Corrected-source soak and controls

Final reviewed source (`release-post-review.json`) passes **16/16 control scripts**, including all3review regressions, previous phase controls and routing persistence. The fresh `child-soak-reviewed/` observation passes **600.042s**,121samples = **118normal/3warning/0critical**, against historical25/96/0.48real child tasks in24batches completed over619.804s. Peak Lane A process RSS **13,163,429,888B**; device-wide GPU in-use **14,209,581,056B** and allocated **15,121,711,104B**.

Child inference p50 **24.970s**, p99 **28.941s**;3013generated tokens and **4.861tok/s** over full load time, including actual retrieval/memory/executor work.64-token cap; this workload is distinct from the fixed32-token HTTP scaling protocol. Source and frozen hashes held; owned runtimes stopped. Prior soak results remain intact and are not substituted for this final revision.

### Corrected-source quality and delivery checks — 2026-09-28

`regressions-reviewed/`, `recall-slot-reviewed/` and `final-verification-reviewed.json`
use the final source snapshot `release-post-review.json`.

| Gate | Required | Measured |
|---|---:|---:|
| Recall, unmodified frozen harness on one slot |20/20|20/20|
| Recall, identical requests on each production slot |20/20|20/20 on slot0 and slot1|
| Abstention |20/20|20/20|
| Product category / final lane |20/20 each|20/20 each|
| Callable JSON |20/20|20/20|
| Tools, first pass / post-retry |17/20 /20/20|17/20 /20/20|
| CLI |18/18|18/18|
| Hook items |5/5|5/5|
| Prior phase and new control scripts |all|16/16 exit0|
| Nuke paths outside the allowed root |0|0 (30,030 entries;0 rejected)|
| `check.sh` |exit0|exit0|

The original two-slot frozen recall run remains **FAILED0/20** because its
single-slot metadata assertion rejects before scoring. The separate verifier
replays the frozen one-slot run's complete requests, with only trusted `id_slot`
transport metadata added, and checks the actual two-slot response,4096-token
context and effective greedy sampling. It uses the same aliases/normalization;
no frozen file, question, expected answer or score was edited. Requests match the
accepted baseline after only the previously authorized vault-path normalization.
This is a documented harness compatibility qualification, not a claim that the
unchanged single-slot harness itself passes against a two-slot server.

The corrected-source product routing mean is **6.737s** (p99 **17.885s**), versus
historical5.06s. The earlier6.720s measurement/cache analysis remains above.
Both classification and final lane stay20/20, and r17 still returns
`formal_reasoning:X` and falls back to LaneC. t07/t09/t12 remain the only first-pass
tool misses and all pass their unchanged retries. No prompt/routing/schema/catalog
tuning was attempted. Both installed commands work; frozen hashes and protected
vault files match the snapshot. No live destructive nuke test was performed.

Group10's nine items are covered by controls and actual shared child load;
separate-process execution is implemented but **refused at the measured cap0**.
The failed real dual-model GPU probe is not certification of successful parallel
model processes. The opt-in parent exact-once delegation smoke also remains a
failure, despite correct results after its second batch. All retained failures
are described above; no passing run replaces their evidence.

Deferred: Phase4.5 web/cloud/guard model, MCP, and all Phase4C computer use.
The computer-use Never guard stays enforced and MLX stays closed. The measured
shared configuration is2slots; adding more slots or enabling separate processes
requires new memory and latency measurements.

**FAILED corrected-source latency repeat (`candidate-zero-reviewed/`):**100requests, p506.015766s, p996.729532s,3200tokens/619.565700s=5.164908tok/s. The strict limit is6.725828s (+10% over6.114389s), so this run fails by0.003703s; rounding does not make it a pass. Sources/fixtures held and runtime stopped. Earlier passing runs remain recorded but do not replace this failure. Delivery is held pending diagnosis.

### Final predefined paired latency check — measured 2026-09-28, reviewed 2026-10-04

After the failed6.729532s repeat, one sequential baseline/candidate pair was
specified in `latency-pair-reviewed/plan.json` before measurement. No production
source, model, prompt, sampling or cache change;100requests and4warmups per point.
The candidate had to pass **both** the original6.725828s limit and the fresh
single-slot p99×1.1. This was one diagnostic pair, not a repeat-until-pass loop.

| Configuration | p50 (s) | p99 (s) | Total tok/s |
|---|---:|---:|---:|
| Fresh single-slot baseline |5.964635|6.031705|5.392269|
| Two slots, zero children |5.995245|6.242120|5.301770|

**PASS:** candidate p99 is2.09% above the original baseline and3.49% above the
paired baseline; below both6.725828s and6.634876s limits. All41source snapshot
files and frozen fixtures held. Both runtimes stopped. Evidence:
`latency-pair-reviewed/summary.json` and complete request records.

The earlier failed run remains a failure, with its cause unproven. This pair
establishes a pass for this run; sequential order cannot separate configuration
effects from time-dependent host drift. For100samples, nearest-rank p99 is the
second-largest observation. The metric includes rendering/HTTP/SSE inference,
not CLI startup or memory I/O. No claim of a latency guarantee across host states.

Delivery resumed on2026-10-04: code still matches the measured snapshot; external
planning commits advanced the vault to v37 without expanding this slice. Wired
limit read0 after the pause, so the final health check is held until the user
restores20480. No model was loaded and no sudo command was run by the agent.

**FAILED delivery health check,2026-10-04:** wired limit was restored to20480, but the per-login03:00 backup job was not registered correctly after the pause. Preserved `check-delivery-login-failed.stdout/stderr`; restoring the existing launchd registration before repeating the health check. No benchmark score or source changed.

Final delivery checks PASS after restoring the existing per-login backup job: `check.sh` exits0, Python3.12.13 and wired20480 verified, both owned runtime ports closed, all41source hashes and frozen fixtures unchanged. Fresh nuke dry-run lists30090entries,0outside `~/Kildall/code`,0rejections, including the3outward Python link objects. No live deletion. See `delivery-verification.json`, `check-delivery.stdout` and `nuke-delivery.json`.

## Routing slot isolation slice — 2026-10-06

Evidence: `.session/routing-slot-fix-20261006/`. Fresh baseline at main3b6b890; candidates A/B/C in user order, stop at first full pass. One predefined100-request interactive latency run per candidate; failed runs remain failures. No HF sync; PR only, no merge.

**FAILED before inference:** baseline setup omitted `bench_cases.json` from the source manifest (the snapshot collected Python files), causing KeyError in fixture verification. `baseline-setup-failed/`, its log and the original manifest are retained. Added the missing hash only after checking the frozen expected SHA; no model loaded, no fixture or production source changed. Corrected baseline follows.

Fresh main3b6b890 baseline: mean6.467455s,p500.890151s,p9917.538660s;7cold(mean17.013346s),13warm(mean0.788898s);category/lane20/20,r17X→C. Outgoing capture shows all27route/answer generation requests bound toslot0. The source audit corrects the initial diagnosis: the production router already inherits whole-turn slot0, but answers overwrite it; direct unbound generation was an additional escape. Sources/fixtures/wired20480 held and runtimes stopped.

CandidateA deterministic wire isolation passes: compact/fallback router calls use0; JSON/native-tool/benchmark requests use1; unowned or mismatched slot overrides are refused, and competing work requests serialize. **FAILED control adaptation:** the old cancellation-stream test used an unconfigured fake endpoint without a trusted slot, so the new admission guard correctly refused it before connection. Retained `controls-a-phase44.log`; the test now binds its fake endpoint inside its worker before exercising the unchanged real-socket cancellation assertion. No production bypass was added.

**FAILED initial control batch (`controls-a/`):** routing mocked-response tests supplied only template/tokenize/completion responses; the new router lease made a real slot-idle metadata call against that mocked sequence. Added trusted fake-slot bindings to those two response-validation unit blocks, preserving every assertion and fixture. Wire-level ownership is separately tested through actual local HTTP in test_slot_isolation.py.

Corrected deterministic control batch passes all17scripts (slot isolation, Phase3/4.1/4.2/4.3/4.4, grammar, transport, routing, benchmark, shell, image, nuke, rename, health and memory controls). Both earlier test-setup failures remain recorded. CandidateA is under final read-only review before source freeze and live gates.

- CandidateA review found a failed-stream handoff gap before live measurement: serialized children could reuse a busy pinned slot before cancellation drained. Added cancellable idle drain before each child inference; focused local HTTP test covers truncated stream followed by queued child and cancellation during idle wait. Phase4.4 controls pass after updating the fake preflight server to expose its slot metadata.

CandidateA paired routing PASS: mean1.8547578999999998s,p500.951048s,p9919.150323s; {"cold": 1, "warm": 19}; group means {"cold": 19.150323, "warm": 0.9444650000000001}s. Category/lane20/20,r17X→C. All20router request bodies match baseline byte-content after removing only id_slot. No routing/prompt change. Runtime stopped and hashes/wired held.

Retained child-drain test evidence: `audit/child-drain-review.md`. Initial control failed because cancelling an in-flight metadata HTTP request raised RemoteDisconnected rather than InterruptedError; the corrected assertion accepts transport errors only with cancellation set. Corrected test exits0; deliberately removing the drain exits1 at the queued-child overlap assertion. This intentional negative control is evidence the regression detects the bug, not a product pass.

CandidateA latency setup FAILED during the first warmup: original request intentionally lacks transport metadata (native_request owns id_slot), so a harness assertion raised KeyError. Zero measured samples; stopped runtime and retained candidate-a-latency-setup-failed/, its log and latency_a_setup_failed.py. Corrected only instrumentation to observe admitted wire slots; same predeclared100 measured requests/4warmups/6.726s gate, unchanged production source. This is not a failed percentile re-run.

CandidateA interactive latency FAILED its one100-request measured run: p50=6.3340627499856055s,p99=7.0369937919895165s >6.726s; 4.9200661913853425tok/s. No repeat. Routing remains a pass1.854758s mean; no winner. CandidateA soak/remaining live regressions skipped after hard latency failure; deterministic controls passed. Full source snapshot/diff retained. Proceeding to candidateB: np3,c12288,router0/work1-2, unchanged cache768 and4096 per slot.

CandidateB controls pass: actual local HTTP shows simultaneous children on1and2, router0 untouched; A/one-slot and child-drain controls retained. Phase4.4 controls exit0. Froze B source before measurement. np3/c12288, cache768/checkpoints3/Q8 KV/4096 per slot unchanged otherwise; separate-process cap0. Starting same20-case routing protocol; then one100-sample latency run and600s real-child memory soak.

CandidateB routing PASS: {"exit": 0, "category": 20, "lane": 20, "mean_s": 1.6175913000000002, "p50_s": 0.829976, "p99_s": 16.613006000000002, "counts": {"cold": 1, "warm": 19}, "group_mean_s": {"cold": 16.613006000000002, "warm": 0.8283589473684211}, "r17_X_to_C": true, "quality_passed": true, "paired_baseline_mean_s": 6.46745475, "speed_passed": true}. All20router bodies identical to baseline after removing only slot metadata. No source or fixture drift.

CandidateB single predefined interactive run PASS: {"n": 100, "p50_s": 6.003025332989637, "p99_s": 6.263291249983013, "total_tokens": 3200, "wall_s": 601.0925327500154, "total_tok_s": 5.323639582345017, "passed": true, "limit_s": 6.726, "children": 0, "work_slot": 1}. All104 warmup/measured native requests used workslot1; no retries. Sequential host variation is not separated from configuration effects. The candidate meets the fixed6.726s gate; A remains failed.

CandidateB real-child soak PASS: {"passed": true, "observation_s": 600.0354559999832, "load_wall_s": 614.5797110410058, "counts": {"normal": 18, "warning": 103, "critical": 0}, "peak_process_rss_bytes": 13207650304, "peak_device_gpu_in_use_bytes": 14655586304, "peak_device_gpu_allocated_bytes": 15628763136, "batches": 25, "children": 50, "inference_p50_s": 24.77534566700342, "inference_p99_s": 25.687578000011854, "total_generated_tokens": 3178, "total_tok_s": 5.171012930540654, "max_tokens_per_reply": 64, "actual_memory_and_executor": true}. Requested4.4 comparison121normal/0warning/0critical; warning pressure is higher, critical remains0. Device-wide GPU figures are separate from process RSS, and shared-machine pressure cannot isolate configuration effects. Actual wire capture uses router0 and child work1/2 only; child audit parents and terminal outcomes verified. Router prefix after soak: {"cache_n": 3888, "prompt_n": 1, "prompt_ms": 70.091, "prompt_per_token_ms": 70.091, "prompt_per_second": 14.267166968655035, "predicted_n": 6, "predicted_ms": 375.724, "predicted_per_token_ms": 75.1448, "predicted_per_second": 13.307640714992921}. Owned runtimes stopped, source/frozen hashes and wired20480 held.

CandidateB v38 recall PASS: frozen harness20/20 on one slot; identical requests20/20 on each production answer slot1and2. Source/frozen hashes held, only historical vault-path normalization allowed, actual slot metadata confirms4096 per slot and sampling. Owned runtimes stopped. Resumed with wired20480 verified; remaining quality/CLI gates next.

Evidence-writer failure after CandidateB quality completed: t07 regex_examples are Python tuples, so atomic_json compared decoded arrays against tuples and failed its read-back check. Complete40-case quality.json.tmp retained and recovered byte-identically as quality.recovered.json; frozen argument scores independently recomputed without inference: category20,callable20,tools17first/20retry,accepted20. Original runner exits1 and stays a failure; CLI had not started. Corrected only evidence serialization to canonical JSON as the prior Phase4.4 runner did. CLI will run separately.

CandidateB live no-drop gates complete: frozen1-slot recall20/20 plus workslot1and2 each20/20; abstention20/20; product category/lane20/20,r17X->C; callable20/20; tools17/20first,20/20post-retry and accepted20 (same t07/t09/t12 misses); CLI18/18. Quality evidence publication failure remains retained separately; no inference rerun. CLI-owned runtimes stopped; running final17 deterministic control scripts, then nuke dry-run/check.sh/delivery verification. C will not run if final controls pass.

### Qualified result — candidate B, completed 2026-10-07

**All required gates pass.** Keep three slots (`-np 3 -c 12288`), 4096 tokens per
slot, router-only slot0 and workslots1–2. The parent lends its workslot while
waiting: **two concurrent shared children**, at most two tasks per batch;
**separate-process cap0**. A's two-slot option reduces work concurrency to one
and failed the fixed interactive latency gate. C was not tried, following the
stop-at-first-full-pass rule. No merge is authorized; delivery stops at the PR.

| Paired product routing, same20cases | Fresh main | A:2slots | B:3slots |
|---|---:|---:|---:|
| Mean(s) |6.467455|1.854758|1.617591|
| p50(s) |0.890151|0.951048|0.829976|
| p99(s), nearest rank |17.538660|19.150323|16.613006|
| Cold / warm |7 / 13|1 / 19|1 / 19|
| Cold mean(s) |17.013346|19.150323|16.613006|
| Warm mean(s) |0.788898|0.944465|0.828359|
| Category / final lane |20 / 20|20 / 20|20 / 20|
| r17 no-match |X→C|X→C|X→C|

B's routing mean is below both5.06s and the fresh paired main result. The full
20router request bodies match after removing only `id_slot`; prompts, sampling,
GBNF, model and catalog/selection logic did not change. Native completion, JSON
and benchmark transports all enforce ownership, including direct callers.
The pinned b10809 audit is in `audit/runtime-audit.md`: production previously
bound the whole turn to slot0, so answers displaced its router prefix. Non-unified
idle live KV survives eviction of its global768MiB saved-cache snapshot.

| Single predefined interactive run, zero children | A | B |
|---|---:|---:|
| Measured requests / warmups |100 / 4|100 / 4|
| p50(s) |6.334063|6.003025|
| p99(s) |7.036993792|6.263291250|
| Fixed limit(s) |6.726|6.726|
| Verdict |**FAIL**|**PASS**|
| End-to-end total tok/s |4.920066|5.323640|

No failed percentile run was repeated. A's separate instrumentation failure
stopped during its first warmup with0measured samples and is retained separately.
The timing covers template rendering/HTTP/SSE, not CLI launch or memory I/O.
Sequential host variation is not isolated: these results do not show that adding
a slot itself makes interactive inference faster, or guarantee p99 on every host state.

**Memory cost:** B's600.035456s observation has **18normal /103warning /0critical**,
compared with the requested4.4 reference **121 /0 /0**. The zero-critical gate
passes; warning pressure is materially higher. Fifty real children in25batches
completed over614.579711s with actual retrieval, project memory writes and linked
executor audit rows. Child inference p50/p99=24.775346/25.687578s;3178generated
tokens,5.171013tok/s over the full load interval. All25native requests per workslot
were pinned to1or2; only the two routing probes used0. The post-soak router kept
3888cached tokens and completed in0.669361s.

Peak Lane A process RSS=13,207,650,304B (13.208GB).
Device-wide GPU in-use=14,655,586,304B (14.656GB),
allocated=15,628,763,136B (15.629GB), reported separately.
Fresh ready-state A→B process RSS rose84,312,064B; device-wide GPU in-use rose
178,143,232B and allocated311,115,776B. These are sequential observations,
not an isolated per-slot physical-RAM estimate: mmap, paging and other GPU users
make RSS/device deltas different quantities. See `candidate-b-memory-ready-comparison.json`.

| Remaining gate | Result |
|---|---|
| Untouched frozen recall, one slot |20/20|
| Same recall requests, every answer slot |slot1:20/20; slot2:20/20|
| Abstention |20/20|
| Additional frozen category/callable JSON |20/20 each|
| Exact tools |17/20 first-pass;20/20 post-retry;20/20 accepted|
| Known first-pass misses |t07,t09,t12 unchanged|
| Real CLI/control |18/18|
| Hooks |5/5|
| Phase3/4.1/4.2/4.4 and transport controls |PASS;17deterministic scripts total|
| Live nuke dry-run |30504entries;0outside `~/Kildall/code`;0rejections;all3outward Python link objects included|
| `check.sh`, installed `kildall` and `orbi` help |exit0 each|
| Fixtures/source and runtime cleanup |Frozen hashes hold;40measured Python/config files unchanged;owned runtimes stopped;wired20480|

Recall's complete request bodies match the accepted run with only the already
authorized vault-path normalization. The frozen test file remains unchanged;
production answer slots were checked through actual server metadata. No prompt,
model, catalog, grammar, Q8 KV, embedding flags or per-slot context change.

**Retained failures:** baseline manifest setup; cancellation/routing mock setup;
child-drain cancellation exception expectation and the intentional no-drain
negative control; A latency instrumentation setup and its measured p99 failure;
B's evidence writer after completed quality inference. That last run remains
exit1: its complete temporary JSON was recovered byte-identically, argument
scores recomputed, and CLI run separately. No quality inference was repeated.
A's later live gates were skipped after its latency failure. Full files and
SHA-linked aggregate: `final-gates.json`, under this slice's evidence directory.

Deferred: C (B passed first), long context,4.5/deep research,MCP and4C. Computer-use
Never guard remains enforced; MLX remains closed; HF sync remains paused. External
vault commits33c39a7/674cc4e/69ff785 advanced planning through v41 during this run;
this slice did not author planning or research changes. Router warmth, ops
hardening and other newly queued improvements remain separate work.
