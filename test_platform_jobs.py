"""Darwin job golden checks against 29ab89b; no live launchd or backup changes."""

import ast
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import plistlib
import subprocess
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from kildall_platform import jobs, UnsupportedPlatform
from test_backup_ops import description


ROOT = Path(__file__).resolve().parent


def previous(name):
    return subprocess.check_output(
        ["/opt/homebrew/bin/git", "show", f"29ab89b:{name}"], cwd=ROOT, text=True)


def python_body(source):
    return source.split(".venv/bin/python - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]


def health(body, limit=20480, registered=True, daemon_ok=True, mode=0o100644):
    payload = jobs().backup_payload({"paths": {"code_dir": ROOT}}, ROOT, ROOT / ".venv/bin/python")
    agent = Path.home() / "Library/LaunchAgents/local.kildall.backup.plist"
    daemon = Path("/Library/LaunchDaemons/local.kildall.wiredlimit.plist")
    boot = {"Label": "local.kildall.wiredlimit", "RunAtLoad": True,
            "ProgramArguments": ["/usr/sbin/sysctl", "iogpu.wired_limit_mb=20480"]}
    boot_live = "\n".join([f"path = {daemon}", "program = /usr/sbin/sysctl",
                           *boot["ProgramArguments"], "last exit code = 0"])

    def launchctl(args, **kwargs):
        if args[-1].startswith("system/"):
            return subprocess.CompletedProcess(args, 0 if daemon_ok else 113, boot_live, "")
        return subprocess.CompletedProcess(args, 0 if registered else 113,
                                           description(agent, payload), "")

    def metadata(path):
        return SimpleNamespace(st_mode=mode if path == daemon else 0o100600,
                               st_uid=0 if path == daemon else os.getuid())

    output, errors = io.StringIO(), io.StringIO()
    with patch("subprocess.check_output", return_value=str(limit)), \
            patch("subprocess.run", side_effect=launchctl) as runner, \
            patch("shutil.disk_usage", return_value=SimpleNamespace(free=123456789)), \
            patch.object(Path, "read_bytes", lambda path: plistlib.dumps(boot if path == daemon else payload)), \
            patch.object(Path, "lstat", metadata), \
            patch.object(Path, "cwd", return_value=ROOT), \
            redirect_stdout(output), redirect_stderr(errors):
        try:
            exec(compile(body, "check.sh", "exec"), {})
        except SystemExit as stopped:
            return stopped.code, output.getvalue(), errors.getvalue(), runner.call_args_list
    raise AssertionError("Health check did not exit")


def main():
    backend = jobs()
    old_backup = previous("backup_ops.py")
    old_nodes = {node.name: ast.dump(node) for node in ast.parse(old_backup).body
                 if isinstance(node, ast.FunctionDef)}
    new_nodes = {node.name: ast.dump(node) for node in ast.parse(Path(backend.__file__).read_text()).body
                 if isinstance(node, ast.FunctionDef)}
    for name in ("backup_payload", "registration_matches", "_launchctl", "_write_plist", "schedule_backups"):
        assert old_nodes[name] == new_nodes[name], name

    legacy = ModuleType("legacy_backup")
    exec(compile(old_backup, "legacy_backup.py", "exec"), legacy.__dict__)
    config = {"paths": {"code_dir": ROOT}}
    for env in ({}, {"ORBI_CONFIG": str(ROOT / "legacy.toml")}, {"KILDALL_CONFIG": str(ROOT / "kildall.toml")}):
        with patch.dict(os.environ, env, clear=True):
            expected = legacy.backup_payload(config, ROOT, ROOT / ".venv/bin/python")
            assert backend.backup_payload(config, ROOT, ROOT / ".venv/bin/python") == expected
            path = Path.home() / "Library/LaunchAgents/local.kildall.backup.plist"
            for text in (description(path, expected), "malformed registration"):
                assert backend.registration_matches(text, expected, path) == legacy.registration_matches(text, expected, path)

    installer = ModuleType("legacy_installer")
    installer.__file__ = str(ROOT / "install_wiredlimit.py")
    exec(compile(previous("install_wiredlimit.py"), installer.__file__, "exec"), installer.__dict__)
    for registered in (False, True):
        results = []
        for invoke in (installer.main, lambda: backend.print_wiredlimit_install(
                ROOT / "launchd/local.kildall.wiredlimit.plist")):
            output = io.StringIO()
            with patch("subprocess.run", side_effect=[subprocess.CompletedProcess([], 0),
                      subprocess.CompletedProcess([], 0 if registered else 113)]) as runner, \
                    redirect_stdout(output):
                invoke()
            assert all(call.args[0][0] != "sudo" for call in runner.call_args_list)
            results.append((output.getvalue(), runner.call_args_list))
        assert results[0] == results[1]

    old_check = python_body(previous("check.sh"))
    new_check = python_body((ROOT / "check.sh").read_text())
    for options in ({}, {"limit": 0}, {"limit": 1024}, {"registered": False},
                    {"daemon_ok": False}, {"mode": 0o100666}, {"mode": 0o120777}):
        actual = list(health(new_check, **options))
        # Slice5b2 adds app telemetry; the Darwin job/probe output and calls stay golden.
        lines = actual[1].splitlines(keepends=True)
        assert sum(line.startswith('Prompt cache: ') for line in lines) == 1
        actual[1] = ''.join(line for line in lines if not line.startswith('Prompt cache: '))
        assert health(old_check, **options) == tuple(actual), options

    import backup_ops
    import install_wiredlimit
    for platform in ("linux", "win32"):
        with patch("sys.platform", platform), patch("subprocess.run") as runner:
            for invoke in (install_wiredlimit.main,
                           lambda: backup_ops.schedule_backups(config, ROOT, ROOT / ".venv/bin/python"),
                           lambda: backup_ops.mirror_backup(ROOT / "unused.snapshot"),
                           lambda: backup_ops.nightly_backup(
                               SimpleNamespace(backup=lambda _: ROOT / "unused.snapshot"), ROOT)):
                try:
                    invoke()
                except UnsupportedPlatform as error:
                    assert "not implemented" in str(error)
                else:
                    raise AssertionError("Unsupported jobs call did not refuse")
            runner.assert_not_called()
            output = io.StringIO()
            with redirect_stdout(output):
                try:
                    exec(compile(new_check, "check.sh", "exec"), {})
                except SystemExit as stopped:
                    assert "not implemented" in str(stopped.code)
                else:
                    raise AssertionError("Unsupported health check did not refuse")
            runner.assert_not_called()
    print("PASS: Darwin scheduling AST/payloads, print-only installer output/argv and health output/exit/argv "
          "match 29ab89b; unsupported jobs/health refuse; no live registration changes.")


if __name__ == "__main__":
    main()
