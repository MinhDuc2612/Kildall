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
import os
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import sys

if sys.version_info[:2] != (3, 12):
    raise SystemExit(f"ERROR: Python 3.12.x required; got {platform.python_version()}")
print(f"Python: {platform.python_version()}", flush=True)

if sys.prefix == sys.base_prefix:
    raise SystemExit("ERROR: .venv/bin/python is not running in a virtual environment.")
import mlx.core as mx

device = mx.default_device()
if device != mx.gpu:
    raise SystemExit(f"ERROR: MLX must use a GPU; got {device}")
print(f".venv: OK; MLX: {device}", flush=True)

limit = int(subprocess.check_output(
    ["/usr/sbin/sysctl", "-n", "iogpu.wired_limit_mb"], text=True).strip())
print(f"iogpu.wired_limit_mb: {limit}", flush=True)
failed = limit != 20480
if failed:
    print(f"WARNING: GPU wired limit is {limit}, expected 20480. Run this yourself before benchmarking: "
          "sudo sysctl iogpu.wired_limit_mb=20480", file=sys.stderr)
free = shutil.disk_usage("/System/Volumes/Data").free
print(f"Free disk (/System/Volumes/Data): {free / 1e9:.2f} GB ({free / 2**30:.2f} GiB)")
print("Recorded baseline: 19.48 tok/s (qwen3:8b, 2026-09-06; not re-measured)")

root = Path.cwd()
try:
    daemon = Path("/Library/LaunchDaemons/local.kildall.wiredlimit.plist")
    expected_daemon = {"Label": "local.kildall.wiredlimit", "RunAtLoad": True,
                       "ProgramArguments": ["/usr/sbin/sysctl", "iogpu.wired_limit_mb=20480"]}
    metadata = daemon.lstat()
    loaded = subprocess.run(["/bin/launchctl", "print", "system/local.kildall.wiredlimit"],
                            text=True, capture_output=True)
    live = {line.strip() for line in loaded.stdout.splitlines()}
    required = {f"path = {daemon}", "program = /usr/sbin/sysctl",
                "/usr/sbin/sysctl", "iogpu.wired_limit_mb=20480", "last exit code = 0"}
    if not (stat.S_ISREG(metadata.st_mode) and metadata.st_uid == 0
            and not metadata.st_mode & 0o022
            and plistlib.loads(daemon.read_bytes()) == expected_daemon
            and loaded.returncode == 0 and required <= live):
        raise ValueError("Wired-limit daemon is missing or mismatched")
except (OSError, ValueError, TypeError):
    failed = True
    print(f"WARNING: Boot wired-limit daemon is not verified. Print the installation commands: "
          f"{root}/.venv/bin/python {root}/install_wiredlimit.py", file=sys.stderr)
else:
    print("Boot wired-limit daemon: installed, registered, last exit 0")
if limit != 20480:
    print(f"Print the installation commands: {root}/.venv/bin/python {root}/install_wiredlimit.py",
          file=sys.stderr)
registration = f"{root}/.venv/bin/kildall --schedule-backups"
service = f"gui/{os.getuid()}/local.kildall.backup"
job = subprocess.run(["/bin/launchctl", "print", service], text=True, capture_output=True)
try:
    from backup_ops import backup_payload, registration_matches
    path = Path.home() / "Library/LaunchAgents/local.kildall.backup.plist"
    schedule = plistlib.loads(path.read_bytes())
    expected = backup_payload({"paths": {"code_dir": root}}, root, root / ".venv/bin/python")
    metadata = path.lstat()
    if not (stat.S_ISREG(metadata.st_mode) and metadata.st_uid == os.getuid()
            and not metadata.st_mode & 0o022 and schedule == expected
            and job.returncode == 0 and registration_matches(job.stdout, expected, path)):
        raise ValueError("Backup job does not match the configured schedule")
except (OSError, ValueError, KeyError, TypeError):
    failed = True
    print(f"WARNING: Nightly backup registration is missing or mismatched. Run: {registration}", file=sys.stderr)
else:
    print("Nightly backup: verified permanent LaunchAgent, 03:00 plus login catch-up")
raise SystemExit(1 if failed else 0)
PY
