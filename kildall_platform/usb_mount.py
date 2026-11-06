#!/usr/bin/python3
"""Kildall USB mount guard; also installed on the internal disk as the launcher."""

import os
from pathlib import Path
import sys
import tempfile


DRIVE = Path("/Volumes/ES2TB")
CODE = DRIVE / "Kildall/code"
MESSAGE = "Kildall drive ES2TB is not mounted"


def require_drive():
    if not os.path.ismount(DRIVE):
        raise RuntimeError(MESSAGE)


def launcher_path():
    return Path.home() / "Library/Application Support/Kildall/launcher.py"


def install_launcher():
    require_drive()
    path = launcher_path()
    if path.is_symlink():
        raise RuntimeError("Kildall launcher must not be a symlink")
    content = Path(__file__).read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            temporary.chmod(0o700)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
    if path.read_bytes() != content:
        raise OSError("Kildall launcher verification failed")
    return path


def main():
    try:
        require_drive()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1
    interpreter = str(CODE / ".venv/bin/python")
    os.execv(interpreter, [interpreter, str(CODE / "kildall.py"), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
