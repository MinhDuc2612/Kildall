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

import cloud
r={'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'READY','tool_calls':None}}]}
assert cloud.validate_message(r,[])=={'role':'assistant','content':'READY'}
