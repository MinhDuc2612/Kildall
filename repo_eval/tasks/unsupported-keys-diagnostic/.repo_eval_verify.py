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

import cloud_keys
out=io.StringIO()
with patch.object(kildall,'require',side_effect=kildall.UnsupportedPlatform('Secure key store not implemented on linux')),patch.object(cloud_keys,'import_keys') as read,contextlib.redirect_stderr(out):
 assert kildall.cloud_main(['keys','import'])==1
assert 'not implemented on linux' in out.getvalue()
read.assert_not_called()
