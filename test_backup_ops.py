"""Real SQLite/copy gates; launchd migration uses a contained fake service."""

from contextlib import closing, redirect_stderr, redirect_stdout
import hashlib
import io
import os
from pathlib import Path
import plistlib
import shutil
import sqlite3
import subprocess
import tempfile
from unittest.mock import patch

import backup_ops as ops
from memory import Memory


def rejects(action, error=Exception):
    try:
        action()
    except error:
        return
    raise AssertionError("Expected rejection")


def description(path, payload, running=False):
    return "\n".join([
        f"path = {path}", f"program = {payload['ProgramArguments'][0]}",
        "arguments = {", *payload["ProgramArguments"], "}",
        f"working directory = {payload['WorkingDirectory']}",
        f"KILDALL_CONFIG => {payload['EnvironmentVariables']['KILDALL_CONFIG']}",
        f"stdout path = {payload['StandardOutPath']}",
        f"stderr path = {payload['StandardErrorPath']}",
        '"Hour" => 3', '"Minute" => 0',
        "state = running" if running else "state = not running",
    ])


class Service:
    def __init__(self, path=None):
        self.path = path
        self.calls = []
        self.running = self.fail_bootstrap = self.bad_registration = False

    def __call__(self, *arguments):
        self.calls.append(arguments)
        command, code, output = arguments[0], 0, ""
        if command == "print":
            if self.path is None:
                code = 113
            elif self.bad_registration and "LaunchAgents" in self.path.parts:
                self.bad_registration = False
                output = "malformed registration"
            else:
                output = description(self.path, plistlib.loads(self.path.read_bytes()), self.running)
        elif command == "bootout":
            assert self.path is not None
            self.path = None
        elif command == "bootstrap":
            assert self.path is None
            path = Path(arguments[2])
            assert path.is_file()
            if self.fail_bootstrap and "LaunchAgents" in path.parts:
                self.fail_bootstrap, code = False, 5
            else:
                self.path = path
        else:
            raise AssertionError("Unexpected launchctl command")
        return subprocess.CompletedProcess(arguments, code, output, "")


def scheduling(root):
    home, code = root / "home", root / "code"
    code.mkdir()
    interpreter = code / "python3.12"
    interpreter.write_bytes(b"not executed")
    (code / "python").symlink_to(interpreter.name)
    config = {"paths": {"code_dir": code}}
    with patch.object(Path, "home", return_value=home), \
         patch.dict(os.environ, {"KILDALL_CONFIG": str(code / "kildall.toml")}), \
         redirect_stdout(io.StringIO()):
        path = home / "Library/LaunchAgents/local.kildall.backup.plist"
        legacy = code / ".session" / path.name
        service = Service()
        with patch.object(ops, "_launchctl", side_effect=service):
            assert ops.schedule_backups(config, code, interpreter) == path
            payload = plistlib.loads(path.read_bytes())
            assert payload == ops.backup_payload(config, code, interpreter)
            assert payload["ProgramArguments"] == [str(code / "python"), str(code / "kildall.py"), "--backup"]
            assert payload["RunAtLoad"] is True
            assert payload["StartCalendarInterval"] == {"Hour": 3, "Minute": 0}
            assert service.path == path
            before = len(service.calls)
            service.running = True
            ops.schedule_backups(config, code, interpreter)
            assert [entry[0] for entry in service.calls[before:]] == ["print"]
            service.running = False

        legacy.parent.mkdir()
        legacy_payload = dict(payload, StandardOutPath=str(code / ".session/backup.log"),
                              StandardErrorPath=str(code / ".session/backup.err"))
        del legacy_payload["RunAtLoad"]
        legacy_bytes = plistlib.dumps(legacy_payload)
        path.unlink()
        for failure in ("fail_bootstrap", "bad_registration"):
            legacy.write_bytes(legacy_bytes)
            service = Service(legacy)
            setattr(service, failure, True)
            with patch.object(ops, "_launchctl", side_effect=service):
                rejects(lambda: ops.schedule_backups(config, code, interpreter), RuntimeError)
            assert service.path == legacy and legacy.read_bytes() == legacy_bytes
            assert not path.exists()
            assert [call[0] for call in service.calls][-2:] == ["bootstrap", "print"]

        service = Service(legacy)
        service.running = True
        with patch.object(ops, "_launchctl", side_effect=service):
            rejects(lambda: ops.schedule_backups(config, code, interpreter), RuntimeError)
        assert len(service.calls) == 1 and legacy.is_file() and not path.exists()
        service.running = False
        with patch.object(ops, "_launchctl", side_effect=service):
            ops.schedule_backups(config, code, interpreter)
        assert service.path == path and not legacy.exists()
        assert [call[0] for call in service.calls][-4:] == ["print", "bootout", "bootstrap", "print"]
        assert ops.registration_matches(description(path, payload), payload, path)
        assert not ops.registration_matches(description(path, dict(payload, ProgramArguments=["foreign"])), payload, path)
        foreign = dict(payload, ProgramArguments=["foreign"])
        path.write_bytes(plistlib.dumps(foreign))
        service = Service(path)
        with patch.object(ops, "_launchctl", side_effect=service):
            rejects(lambda: ops.schedule_backups(config, code, interpreter), RuntimeError)
        assert len(service.calls) == 1 and plistlib.loads(path.read_bytes()) == foreign


def copying(root):
    memory = Memory(root / "memory.sqlite3")
    with closing(memory._connect()) as db:
        db.execute("INSERT INTO memories(text,scope,project,tier,tags,created,vector,embedding_truncated) "
                   "VALUES('verified record','global',NULL,'L3','',0,zeroblob(4096),0)")
        db.commit()
    backup_dir = root / "snapshots"
    snapshot = memory.backup(backup_dir)
    volume = root / "volume"
    volume.mkdir()
    missing = root / "absent-volume"
    errors = io.StringIO()
    with redirect_stderr(errors):
        assert ops.mirror_backup(snapshot, missing) is None
    assert "WARNING" in errors.getvalue() and "not mounted" in errors.getvalue()
    assert not missing.exists()
    with patch.object(ops.os.path, "ismount", return_value=True), redirect_stdout(io.StringIO()):
        copied = ops.mirror_backup(snapshot, volume)
        assert copied.parent == volume / "kildall-backups"
        for suffix in (".sqlite3", ".md"):
            assert hashlib.sha256(copied.with_suffix(suffix).read_bytes()).digest() == hashlib.sha256(snapshot.with_suffix(suffix).read_bytes()).digest()
        with closing(sqlite3.connect(copied.as_uri() + "?mode=ro", uri=True)) as db:
            Memory._verify_snapshot(db)
            assert db.execute("SELECT text FROM memories").fetchall() == [("verified record",)]
        namespace = ops._SNAPSHOT.fullmatch(snapshot.name)[1]
        old = copied.parent / (namespace + "20000101T000000-" + "a" * 32 + ".sqlite3")
        shutil.copyfile(snapshot, old)
        old.with_suffix(".md").write_text("old")
        unrelated = copied.parent / ("kildall-memory-" + "f" * 16 + "-20000101T000000-" + "b" * 32 + ".sqlite3")
        unrelated.write_text("another database namespace")
        linked = copied.parent / (namespace + "20000101T000000-" + "c" * 32 + ".sqlite3")
        linked.symlink_to(snapshot)
        assert ops.mirror_backup(snapshot, volume) == copied
        assert not old.exists() and not old.with_suffix(".md").exists()
        assert unrelated.is_file() and linked.is_symlink() and snapshot.is_file()
        copied.unlink()
        copied.symlink_to(snapshot)
        rejects(lambda: ops.mirror_backup(snapshot, volume))
        copied.unlink()
        copied.write_text("corrupt existing copy")
        rejects(lambda: ops.mirror_backup(snapshot, volume))
        corrupt = backup_dir / (namespace + "20990101T000000-" + "d" * 32 + ".sqlite3")
        corrupt.write_text("not a sqlite database")
        rejects(lambda: ops.mirror_backup(corrupt, volume))
        assert not (copied.parent / corrupt.name).exists()
        linked_volume = root / "linked-volume"
        linked_volume.symlink_to(volume, target_is_directory=True)
        rejects(lambda: ops.mirror_backup(snapshot, linked_volume))
        another = root / "another-volume"
        another.mkdir()
        (another / "kildall-backups").symlink_to(copied.parent, target_is_directory=True)
        rejects(lambda: ops.mirror_backup(snapshot, another))
    errors = io.StringIO()
    with patch.object(ops.os.path, "ismount", return_value=False), redirect_stderr(errors):
        local = ops.nightly_backup(memory, backup_dir)
    assert local != snapshot and local.is_file() and "not mounted" in errors.getvalue()
    errors = io.StringIO()
    private = "private exception payload"
    with patch.object(ops, "mirror_backup", side_effect=OSError(private)), redirect_stderr(errors):
        local = ops.nightly_backup(memory, backup_dir)
    assert local.is_file() and "verified local backup retained" in errors.getvalue()
    assert private not in errors.getvalue()
    with patch.object(memory, "backup", side_effect=OSError("local failure")), \
         patch.object(ops, "mirror_backup") as mirror:
        rejects(lambda: ops.nightly_backup(memory, backup_dir), OSError)
        mirror.assert_not_called()


def main():
    with tempfile.TemporaryDirectory(prefix="kildall-backup-ops-") as directory:
        root = Path(directory).resolve()
        scheduling(root)
        copying(root)
    print("PASS: permanent schedule/idempotence, migration and rollback, active/foreign job refusal; "
          "verified SQLite and Markdown copies, scoped retention, symlink/corruption refusal, "
          "unmounted/copy-failure isolation; no live launchd changes")


if __name__ == "__main__":
    main()
