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

p=WORK/'repo';(p/'.git').mkdir(parents=True);(p/'.git/commondir').write_text('../../different')
(p/'.git/config').write_text('[core]\n bare=false\n')
rejected(lambda:permissions.git_repository(p),PermissionError)
