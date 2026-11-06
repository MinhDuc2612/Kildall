"""Check health failures without changing sysctl or launchd registration."""

from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import plistlib
import subprocess
from types import SimpleNamespace
from unittest.mock import patch
from backup_ops import backup_payload


def main():
    root = Path(__file__).resolve().parent
    body = (root / "check.sh").read_text().split(".venv/bin/python - <<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
    schedule = backup_payload({"paths": {"code_dir": root}}, root, root / ".venv/bin/python")
    agent = Path.home() / 'Library/LaunchAgents/local.kildall.backup.plist'
    daemon = Path('/Library/LaunchDaemons/local.kildall.wiredlimit.plist')
    boot = dict(Label='local.kildall.wiredlimit', RunAtLoad=True,
                ProgramArguments=['/usr/sbin/sysctl', 'iogpu.wired_limit_mb=20480'])
    boot_live = '\n'.join([f'path = {daemon}', 'program = /usr/sbin/sysctl',
                          *boot['ProgramArguments'], 'last exit code = 0'])
    live = "\n".join([f"path = {agent}",
        f"program = {schedule['ProgramArguments'][0]}", 'arguments = {', *schedule["ProgramArguments"], '}',
        f"working directory = {root}", f"KILDALL_CONFIG => {root / 'kildall.toml'}",
        f"stdout path = {schedule['StandardOutPath']}", f"stderr path = {schedule['StandardErrorPath']}",
        '"Hour" => 3', '"Minute" => 0'])

    def run(limit, registered=True, text=live, optimize=0, daemon_ok=True, owner=0, mode=0o100644):
        output, errors = io.StringIO(), io.StringIO()
        def launchctl(args, **kwargs):
            if args[-1].startswith('system/'):
                return subprocess.CompletedProcess(args, 0 if daemon_ok else 113, boot_live, '')
            return subprocess.CompletedProcess(args, 0 if registered else 113, text, '')
        def read_bytes(path):
            return plistlib.dumps(boot if path == daemon else schedule)
        def metadata(path):
            return SimpleNamespace(st_mode=mode if path == daemon else 0o100600,
                                   st_uid=owner if path == daemon else os.getuid())
        with patch("subprocess.check_output", return_value=str(limit)), \
                patch("subprocess.run", side_effect=launchctl), \
                patch.object(Path, "read_bytes", read_bytes), \
                patch.object(Path, "lstat", metadata), \
                patch.object(Path, "cwd", return_value=root), \
                redirect_stdout(output), redirect_stderr(errors):
            try:
                exec(compile(body, "check.sh", "exec", optimize=optimize), {})
            except SystemExit as exit:
                return exit.code, output.getvalue(), errors.getvalue()
        raise AssertionError("Health check did not set an exit status")

    for optimize in (0, 1):
        code, output, errors = run(20480, optimize=optimize)
        assert code == 0 and "Nightly backup: verified" in output and not errors
        code, output, errors = run(0, optimize=optimize)
        assert code != 0 and "wired limit is 0" in errors
        assert "sudo sysctl iogpu.wired_limit_mb=20480" in errors
        for options in ({'daemon_ok': False}, {'owner': os.getuid()}, {'mode': 0o100666}, {'mode': 0o120777}):
            code, output, errors = run(20480, optimize=optimize, **options)
            assert code != 0 and 'install_wiredlimit.py' in errors
        code, output, errors = run(1024, optimize=optimize)
        assert code != 0 and 'install_wiredlimit.py' in errors
        code, output, errors = run(20480, registered=False, optimize=optimize)
        assert code != 0 and "Nightly backup: verified" not in output
        assert f"{root}/.venv/bin/kildall --schedule-backups" in errors
        for changed in (live.replace('"Hour" => 3', '"Hour" => 30'),
                        live.replace(str(root / "kildall.py"), "/unrelated/kildall.py")):
            code, output, errors = run(20480, text=changed, optimize=optimize)
            assert code != 0 and "Nightly backup: verified" not in output
    import install_wiredlimit
    for registered in (False, True):
        with patch('subprocess.run', side_effect=[subprocess.CompletedProcess([], 0),
                  subprocess.CompletedProcess([], 0 if registered else 113)]) as runner, \
                redirect_stdout(io.StringIO()) as output:
            install_wiredlimit.main()
        assert all(call.args[0][0] != 'sudo' for call in runner.call_args_list)
        assert 'sudo /usr/bin/install -o root -g wheel -m 0644' in output.getvalue()
        assert ('bootout' in output.getvalue()) == registered
    print("PASS: exact wired limit, installed daemon ownership/mode, permanent backup schedule and print-only installer; no system settings changed.")


if __name__ == "__main__":
    main()
