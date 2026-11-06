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

opened=[]
def terminal(path,mode,*args,**kwargs):
 assert path=='/dev/tty'
 opened.append(mode)
 if mode=='r+':raise io.UnsupportedOperation('File or stream is not seekable')
 return io.StringIO('yes\n' if mode=='r' else '')
with patch('builtins.open',side_effect=terminal):
 assert permissions.terminal_confirm({'change':'preview'}) is True
assert sorted(opened)==['r','w']

with patch('builtins.open',side_effect=lambda path,mode,*args,**kwargs:io.StringIO('no\n' if mode=='r' else '')):
 assert permissions.terminal_confirm({'change':'preview'}) is False


for answer in ('\n','y\n','YES\n','yes please\n',' yes\n','yes \n'):
 with patch('builtins.open',side_effect=lambda path,mode,*args,**kwargs:io.StringIO(answer if mode=='r' else '')):
  assert permissions.terminal_confirm({'change':'preview'}) is False,answer
