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

record={'pid':123,'started':'owner','model':'model.gguf','port':8123}
with patch.object(kildall,'process_start',return_value='owner'),patch.object(kildall.system(),'process_command',return_value=SimpleNamespace(returncode=0,stdout='llama-server -m model.gguf --port 9999')):
 assert not kildall.owns_server(record)
