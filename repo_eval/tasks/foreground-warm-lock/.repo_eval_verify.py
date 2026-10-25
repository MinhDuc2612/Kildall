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

import router_warmth as warmth
base=WORK/'warm';base.with_suffix('.sock').touch()
entered=[]
def lock(fd,*,exclusive=True,nonblocking=False):
 assert nonblocking,'Foreground would wait for the maintenance lock'
 raise BlockingIOError()
with patch.object(warmth,'files',return_value=base),patch.object(warmth,'notify'),patch.object(warmth.system(),'lock',side_effect=lock),patch.object(warmth.system(),'unlock'):
 with warmth.foreground('http://127.0.0.1:8123/completion'):entered.append(True)
assert entered==[True]
