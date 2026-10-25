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
 if args[:2]==('ls-files','-v'):return b'h file.txt\0'
 if args[:2]==('symbolic-ref','HEAD'):return b'refs/heads/feature\n'
 return b''
with patch.object(permissions,'git_repository',return_value=WORK),patch.object(permissions,'git',side_effect=git),patch.object(git_tools,'revision',return_value='a'*40),patch.object(permissions,'authorize'):
 rejected(lambda:git_tools.execute('git_switch',{'path':str(WORK),'name':'feature'},record,str(WORK)),PermissionError)
