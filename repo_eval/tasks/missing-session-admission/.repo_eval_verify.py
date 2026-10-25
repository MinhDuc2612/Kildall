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

db=WORK/'state.db';kildall.initialize(db)
with patch.object(kildall,'process_start',return_value='owner'),patch.object(threading.Thread,'start'):
 rejected(lambda:kildall.Task(db,'deleted-session'),RuntimeError)
