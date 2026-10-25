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

import git_tools
record={'task':None,'requested':set(),'update':Mock()}
def git(repo,*args):
 return b'160000 '+b'a'*40+b' 0\tmodule\0' if args[:2]==('ls-files','--stage') else b''
with patch.object(permissions,'git_repository',return_value=WORK),patch.object(permissions,'git',side_effect=git),patch.object(permissions,'authorize'):
 rejected(lambda:git_tools.execute('git_read',{'path':str(WORK),'action':'diff'},record,str(WORK)),PermissionError)
