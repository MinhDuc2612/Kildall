"""An absent USB drive refuses entry points before any work or path creation."""

from contextlib import redirect_stderr
import io
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
from unittest.mock import Mock, patch

import backup_ops
import kildall
import permissions
from kildall_platform import usb_mount


def main():
    with patch.object(usb_mount.os.path, "ismount", return_value=False), \
         patch.object(Path, "mkdir", side_effect=AssertionError("created a path")), \
         patch.object(kildall, "initialize", side_effect=AssertionError("opened database")), \
         patch.object(usb_mount.os, "execv", side_effect=AssertionError("started process")):
        for action in (usb_mount.require_drive, permissions.nuke,
                       lambda: backup_ops.nightly_backup(Mock(), Path("unused")),
                       lambda: backup_ops.schedule_backups({}, Path("unused"), "unused"),
                       usb_mount.install_launcher):
            try:
                action()
            except RuntimeError as error:
                assert str(error) == usb_mount.MESSAGE
            else:
                raise AssertionError("Unmounted drive accepted")
        for argv in (["kildall", "--help"], ["kildall", "nuke"], ["kildall", "--backup"]):
            errors = io.StringIO()
            with patch.object(sys, "argv", argv), redirect_stderr(errors):
                assert kildall.main() == 1
            assert errors.getvalue().strip() == usb_mount.MESSAGE
        errors = io.StringIO()
        with redirect_stderr(errors):
            try:
                runpy.run_path(usb_mount.__file__, run_name="__main__")
            except SystemExit as error:
                assert error.code == 1
            else:
                raise AssertionError("Standalone launcher accepted absent drive")
        assert errors.getvalue().strip() == usb_mount.MESSAGE
    with tempfile.TemporaryDirectory(prefix="kildall-unmounted-") as directory:
        temporary = Path(directory)
        (temporary / "sitecustomize.py").write_text("import os\nos.path.ismount = lambda path: False\n")
        launcher = temporary / "launcher.py"
        launcher.write_bytes(Path(usb_mount.__file__).read_bytes())
        for command in (["/bin/sh", str(kildall.ROOT / "check.sh")],
                        ["/usr/bin/python3", str(launcher), "--backup"]):
            result = subprocess.run(command, cwd=temporary, capture_output=True, text=True,
                                    env=dict(os.environ, PYTHONPATH=str(temporary)))
            assert result.returncode == 1 and not result.stdout
            assert result.stderr.strip() == usb_mount.MESSAGE, result.stderr
    print("PASS: absent USB refuses CLI, nuke, backup and standalone launcher without side effects")


if __name__ == "__main__":
    main()
