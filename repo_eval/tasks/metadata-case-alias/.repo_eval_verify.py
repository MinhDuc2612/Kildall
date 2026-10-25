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

p=WORK/'.GIT/config';p.parent.mkdir();p.write_text('original')
record={'update':Mock(),'requested':set()}
with patch.object(permissions,'terminal_confirm',return_value=True):
 rejected(lambda:permissions.execute('write',{'path':str(p),'content':'changed'},record,str(WORK)),PermissionError)
assert p.read_text()=='original'
