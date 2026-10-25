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

import router_warmth as warmth, subagents
root=WORK/'runtime';directory=root/'.session/router-prefix';directory.mkdir(parents=True)
sentinel=WORK/'sentinel';sentinel.write_bytes(b'preserve')
(directory/'prefix-fixed.pending').symlink_to(sentinel)
def request(endpoint,body):
 if endpoint.endswith('action=save'):(directory/body['filename']).write_bytes(b'overwritten')
 return {}
cfg={'paths':{'code_dir':root},'runtime':{'port':8123,'parallel':3,'context_size':4096}}
with patch.object(warmth,'cache_key',return_value={}),patch.object(warmth,'prefix',return_value=[1]),patch.object(warmth,'valid_file',return_value=False),patch.object(warmth,'warm',return_value={}),patch.object(warmth.uuid,'uuid4',return_value=SimpleNamespace(hex='fixed')),patch.object(subagents,'router_slot',side_effect=lambda cfg:contextlib.nullcontext()),patch.object(kildall,'json_request',side_effect=request):
 rejected(lambda:warmth.initialize(cfg,{},[]),ValueError)
assert sentinel.read_bytes()==b'preserve'
