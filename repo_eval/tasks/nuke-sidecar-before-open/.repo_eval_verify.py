from pathlib import Path
from unittest.mock import Mock, patch
from types import SimpleNamespace
import contextlib, io, json, os, sqlite3, threading, time
import kildall, permissions
WORK=Path.cwd()/'_probe'
WORK.mkdir(exist_ok=True)
def rejected(call, kind=Exception):
    try: call()
    except kind: return
    raise AssertionError('Required failure was silently accepted')

root=WORK/'scope';root.mkdir();outside=WORK/'sentinel';outside.write_text('unchanged')
(root/'kildall.db-wal').symlink_to(outside)
rejected(lambda:permissions.nuke_database(root),PermissionError)
assert outside.read_text()=='unchanged'
(root/'kildall.db-wal').unlink()
assert permissions.nuke_database(root)==root/'kildall.db'
assert not (root/'kildall.db').exists(),'Validation must not open the audit database'
assert outside.read_text()=='unchanged'
