"""Persistent local scheduling and verified, best-effort off-machine snapshots."""

from contextlib import closing
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import sys
import tempfile

from memory import Memory
from kildall_platform import jobs, system, UnsupportedPlatform


_SNAPSHOT = re.compile(r"(kildall-memory-[0-9a-f]{16}-)(\d{8}T\d{6})-[0-9a-f]{32}\.sqlite3")


def backup_payload(config, root, interpreter):
    return jobs().backup_payload(config, root, interpreter)


def registration_matches(output, payload, path):
    return jobs().registration_matches(output, payload, path)


def schedule_backups(config, root, interpreter):
    return jobs().schedule_backups(config, root, interpreter)


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


def mirror_backup(snapshot, mount=None):
    """Copy the just-created verified snapshot; mount is injectable only for tests."""
    snapshot, mount = Path(snapshot), Path(system().backup_volume() if mount is None else mount)
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
    except UnsupportedPlatform:
        raise
    except Exception:
        # Exception text may include private database contents or external path names.
        print("WARNING: off-machine backup failed; verified local backup retained", file=sys.stderr)
    return snapshot
