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
with patch.object(kildall,'json_request',return_value={'tokens_evaluated':2,'timings':{}}):
 rejected(lambda:warmth.warm({'runtime':{'port':8123}},[1,2,3]),ValueError)
