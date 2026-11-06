"""Existing macOS launchd scheduling, registration checks and print-only installer."""

import os
from pathlib import Path
import plistlib
import re
import shlex
import stat
import subprocess
import sys
import tempfile


LABEL = "local.kildall.backup"


def backup_payload(config, root, interpreter):
    root, interpreter = Path(root), Path(interpreter)
    canonical = interpreter.with_name("python")
    if canonical.is_file() and canonical.samefile(interpreter):
        interpreter = canonical
    logs = Path.home() / "Library/Logs/Kildall"
    return {
        "Label": LABEL,
        "ProgramArguments": [str(interpreter), str(root / "kildall.py"), "--backup"],
        "WorkingDirectory": str(config["paths"]["code_dir"]),
        "EnvironmentVariables": {"KILDALL_CONFIG": str(Path(os.environ.get(
            "KILDALL_CONFIG", os.environ.get("ORBI_CONFIG", root / "kildall.toml"))).resolve())},
        "StartCalendarInterval": {"Hour": 3, "Minute": 0},
        "RunAtLoad": True,
        "StandardOutPath": str(logs / "backup.log"),
        "StandardErrorPath": str(logs / "backup.err"),
    }


def registration_matches(output, payload, path):
    lines = {line.strip() for line in output.splitlines()}
    arguments = re.search(r"\barguments = \{\n(.*?)\n\s*\}", output, re.S)
    return bool(arguments and [line.strip() for line in arguments[1].splitlines()
                               if line.strip()] == payload["ProgramArguments"] and {
        f"path = {path}", f"program = {payload['ProgramArguments'][0]}",
        f"working directory = {payload['WorkingDirectory']}",
        f"KILDALL_CONFIG => {payload['EnvironmentVariables']['KILDALL_CONFIG']}",
        f"stdout path = {payload['StandardOutPath']}",
        f"stderr path = {payload['StandardErrorPath']}",
        '"Hour" => 3', '"Minute" => 0',
    } <= lines)


def _launchctl(*arguments):
    return subprocess.run(["/bin/launchctl", *arguments], capture_output=True,
                          text=True, timeout=30)


def _write_plist(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".backup-", delete=False) as file:
        temporary = Path(file.name)
        try:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
            result = subprocess.run(["/usr/bin/plutil", "-lint", str(temporary)],
                                    capture_output=True, timeout=10)
            if result.returncode:
                raise RuntimeError("Backup LaunchAgent plist failed validation")
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def schedule_backups(config, root, interpreter):
    payload = backup_payload(config, root, interpreter)
    directory = Path.home() / "Library/LaunchAgents"
    path = directory / f"{LABEL}.plist"
    legacy = Path(config["paths"]["code_dir"]) / ".session" / path.name
    service = f"gui/{os.getuid()}/{LABEL}"
    existing = _launchctl("print", service)
    previous = None
    if existing.returncode == 0:
        for candidate in (path, legacy):
            if f"path = {candidate}" in {line.strip() for line in existing.stdout.splitlines()}:
                previous = candidate
                break
        if previous is None or previous.is_symlink():
            raise RuntimeError("A different service already owns the backup label")
        old = plistlib.loads(previous.read_bytes())
        identity = ("Label", "ProgramArguments", "WorkingDirectory", "EnvironmentVariables",
                    "StartCalendarInterval")
        if (any(old.get(key) != payload[key] for key in identity)
                or not registration_matches(existing.stdout, old, previous)):
            raise RuntimeError("A different service already owns the backup label")
        if previous == path and old == payload:
            print("Nightly backup: permanent LaunchAgent already registered (03:00 and login).")
            return path
        if any(line.strip() == "state = running" or re.fullmatch(r"pid = \d+", line.strip())
               for line in existing.stdout.splitlines()):
            raise RuntimeError("Backup is running; retry scheduling after it finishes")
    elif existing.returncode != 113:
        raise RuntimeError("Could not inspect the backup LaunchAgent")
    if path.is_symlink():
        raise RuntimeError("Backup LaunchAgent path must not be a symlink")
    saved = path.read_bytes() if path.exists() else None
    directory.mkdir(parents=True, exist_ok=True)
    Path(payload["StandardOutPath"]).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    _write_plist(path, plistlib.dumps(payload))
    stopped = activated = False
    try:
        if plistlib.loads(path.read_bytes()) != payload:
            raise RuntimeError("Published backup LaunchAgent plist verification failed")
        if previous is not None:
            if _launchctl("bootout", service).returncode:
                raise RuntimeError("Could not unload the previous backup LaunchAgent")
            stopped = True
        if _launchctl("bootstrap", f"gui/{os.getuid()}", str(path)).returncode:
            raise RuntimeError("Could not register the permanent backup LaunchAgent")
        activated = True
        registered = _launchctl("print", service)
        if registered.returncode or not registration_matches(registered.stdout, payload, path):
            raise RuntimeError("Permanent backup LaunchAgent verification failed")
    except Exception:
        removed = not activated or _launchctl("bootout", service).returncode == 0
        if saved is None:
            path.unlink(missing_ok=True)
        else:
            _write_plist(path, saved)
        if not removed:
            raise RuntimeError("Backup registration failed; candidate job could not be unloaded") from None
        if stopped:
            restored = _launchctl("bootstrap", f"gui/{os.getuid()}", str(previous))
            checked = _launchctl("print", service)
            if restored.returncode or checked.returncode or not registration_matches(checked.stdout, old, previous):
                raise RuntimeError("Backup registration failed and the previous job could not be restored") from None
        raise
    if previous == legacy:
        legacy.unlink()
        if legacy.exists():
            raise OSError("Legacy backup plist removal could not be verified")
    print("Nightly backup: permanent LaunchAgent registered (03:00 and login).")
    return path


def print_wiredlimit_install(source):
    source = Path(source)
    subprocess.run(["/usr/bin/plutil", "-lint", str(source)], check=True,
                   stdout=subprocess.DEVNULL)
    target = Path("/Library/LaunchDaemons/local.kildall.wiredlimit.plist")
    service = "system/local.kildall.wiredlimit"
    existing = subprocess.run(["/bin/launchctl", "print", service], capture_output=True)
    commands = []
    if existing.returncode == 0:
        commands.append(["sudo", "/bin/launchctl", "bootout", service])
    commands.extend([
        ["sudo", "/usr/bin/install", "-o", "root", "-g", "wheel", "-m", "0644", str(source), str(target)],
        ["sudo", "/bin/launchctl", "bootstrap", "system", str(target)],
        ["sudo", "/bin/launchctl", "kickstart", service],
    ])
    for command in commands:
        print(shlex.join(command))


def check_registrations(root, limit):
    failed = False
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
    return failed
