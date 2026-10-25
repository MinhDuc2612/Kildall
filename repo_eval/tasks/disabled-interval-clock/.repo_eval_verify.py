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
cfg={'paths':{'db_path':WORK/'cloud.db'},'cloud':{'enabled':False}}
c=cloud.Client(cfg)
with patch.object(cloud.time,'time',return_value=2000000000):
 assert c.reserve('llm7',{'min_interval_seconds':0},'fingerprint',1,None)
with patch.object(cloud.time,'time',return_value=1999999990):
 assert c.reserve('llm7',{'min_interval_seconds':0},'fingerprint',1,None)
