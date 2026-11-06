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


for prefix in (b'sk-proj-',b'sk-',b'gsk_',b'AIza',b'nvapi-',b'hf_'):
 assert any(p.search(prefix+b'X'*24) for _,p in secret_scanner.PATTERNS),prefix
assert any(p.search(b'sk-'+b'X'*12) for _,p in secret_scanner.PATTERNS)
for text in (b'a-task-with-a-very-long-description-that-keeps-going-on-and-on',b'dogsk_with_long_underscored_name',b'shf_with_long_underscored_name'):
 assert not any(p.search(text) for _,p in secret_scanner.PATTERNS),text
