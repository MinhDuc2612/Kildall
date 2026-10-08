"""Persistent local scheduling and verified, best-effort off-machine snapshots."""

from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import plistlib
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile

from memory import Memory


LABEL = "local.kildall.backup"
EXTERNAL_VOLUME = Path("/Volumes/KildallC")
_SNAPSHOT = re.compile(r"(kildall-memory-[0-9a-f]{16}-)(\d{8}T\d{6})-[0-9a-f]{32}\.sqlite3")


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


def _regular(path):
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError("Backup files must be regular files, not symlinks")


def _digest(path):
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as file:
        if not stat.S_ISREG(os.fstat(file.fileno()).st_mode):
            raise ValueError("Backup files must be regular files")
        return hashlib.file_digest(file, "sha256").digest()


def _verify(path):
    _regular(path)
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro&immutable=1", uri=True)) as db:
        Memory._verify_snapshot(db)


def mirror_backup(snapshot, mount=EXTERNAL_VOLUME):
    """Copy the just-created verified snapshot; mount is injectable only for tests."""
    snapshot, mount = Path(snapshot), Path(mount)
    if not os.path.ismount(mount):
        print("WARNING: off-machine backup skipped: KildallC is not mounted", file=sys.stderr)
        return None
    if mount.resolve(strict=True) != mount.absolute():
        raise ValueError("Backup mount must not use symlinks")
    match = _SNAPSHOT.fullmatch(snapshot.name)
    if not match or snapshot.resolve(strict=True) != snapshot.absolute():
        raise ValueError("Invalid local snapshot path")
    _verify(snapshot)
    markdown = snapshot.with_suffix(".md")
    _regular(markdown)
    destination = mount / "kildall-backups"
    destination.mkdir(mode=0o700, exist_ok=True)
    if not stat.S_ISDIR(destination.lstat().st_mode):
        raise ValueError("Backup destination must be a directory, not a symlink")
    pending = []
    try:
        # Publish Markdown first; publishing the verified DB marks the pair complete.
        for source in (markdown, snapshot):
            before = _digest(source)
            target = destination / source.name
            if target.exists() or target.is_symlink():
                _regular(target)
                if _digest(target) != before:
                    raise ValueError("Existing off-machine backup does not match")
                if source == snapshot:
                    _verify(target)
                continue
            with tempfile.NamedTemporaryFile(dir=destination, prefix=".backup-", delete=False) as file:
                temporary = Path(file.name)
                pending.append(temporary)
                with os.fdopen(os.open(source, os.O_RDONLY | os.O_NOFOLLOW), "rb") as incoming:
                    shutil.copyfileobj(incoming, file)
                file.flush()
                os.fsync(file.fileno())
            if _digest(temporary) != before or _digest(source) != before:
                raise ValueError("Off-machine backup hash verification failed")
            if source == snapshot:
                _verify(temporary)
            temporary.replace(target)
            if _digest(target) != before:
                raise ValueError("Published off-machine backup hash verification failed")
        cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        for old in destination.iterdir():
            old_match = _SNAPSHOT.fullmatch(old.name)
            if not old_match or old_match[1] != match[1] or not stat.S_ISREG(old.lstat().st_mode):
                continue
            stamp = datetime.strptime(old_match[2], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
            if stamp < cutoff:
                old.unlink()
                mirror = old.with_suffix(".md")
                if mirror.exists() and stat.S_ISREG(mirror.lstat().st_mode):
                    mirror.unlink()
        print("Off-machine backup: SHA-256 and SQLite integrity_check verified")
        return destination / snapshot.name
    finally:
        for temporary in pending:
            temporary.unlink(missing_ok=True)


def nightly_backup(memory, backup_dir):
    snapshot = memory.backup(backup_dir)
    try:
        mirror_backup(snapshot)
    except Exception:
        # Exception text may include private database contents or external path names.
        print("WARNING: off-machine backup failed; verified local backup retained", file=sys.stderr)
    return snapshot
