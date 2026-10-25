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
t=object.__new__(kildall.Task);t.path=db;t.id='gone';t.session='s';t.lock=threading.RLock();t.state='idle';t.tty=False;t.finished=threading.Event();t.watcher=Mock()
t.set=Mock()
rejected(lambda:t.finish('done'),RuntimeError)