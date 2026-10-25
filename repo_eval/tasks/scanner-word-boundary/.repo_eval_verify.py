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

import secret_scanner
ordinary=b'A task-with-a-long-description is ordinary text.'
assert not any(pattern.search(ordinary) for _,pattern in secret_scanner.PATTERNS)
credential=b'sk-'+b'X'*24
assert any(pattern.search(credential) for _,pattern in secret_scanner.PATTERNS)
