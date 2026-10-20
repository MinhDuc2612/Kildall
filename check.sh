#!/bin/sh
set -eu
cd -- "$(dirname -- "$0")"

if [ ! -f .venv/pyvenv.cfg ] || [ ! -x .venv/bin/python ]; then
    printf '%s\n' 'ERROR: .venv is missing or incomplete.' >&2
    exit 1
fi

export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
.venv/bin/python - <<'PY'
import platform
from pathlib import Path
import shutil
import sys
from kildall_platform import jobs, system, UnsupportedPlatform

if sys.version_info[:2] != (3, 12):
    raise SystemExit(f"ERROR: Python 3.12.x required; got {platform.python_version()}")
print(f"Python: {platform.python_version()}", flush=True)

if sys.prefix == sys.base_prefix:
    raise SystemExit("ERROR: .venv/bin/python is not running in a virtual environment.")
try:
    host, scheduler = system(), jobs()
except UnsupportedPlatform as error:
    raise SystemExit(f"ERROR: {error}") from None
device = host.check_gpu()
print(f".venv: OK; MLX: {device}", flush=True)

limit = host.wired_limit()
print(f"iogpu.wired_limit_mb: {limit}", flush=True)
failed = limit != 20480
if failed:
    print(f"WARNING: GPU wired limit is {limit}, expected 20480. Run this yourself before benchmarking: "
          "sudo sysctl iogpu.wired_limit_mb=20480", file=sys.stderr)
volume = host.data_volume()
free = shutil.disk_usage(volume).free
print(f"Free disk ({volume}): {free / 1e9:.2f} GB ({free / 2**30:.2f} GiB)")
print("Recorded baseline: 19.48 tok/s (qwen3:8b, 2026-09-06; not re-measured)")

root = Path.cwd()
failed = scheduler.check_registrations(root, limit) or failed
from kildall import cache_health, settings
print(cache_health(settings()['paths']['db_path']))
raise SystemExit(1 if failed else 0)
PY
