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

def clean(repo,*args):
 if args[0]=='diff':return b'ordinary file diff\n'
 return b'100644 '+b'a'*40+b' 0\tfile.txt\0' if args[:2]==('ls-files','--stage') else b''
with patch.object(permissions,'git_repository',return_value=WORK),patch.object(permissions,'git',side_effect=clean),patch.object(permissions,'authorize'):
 assert git_tools.execute('git_read',{'path':str(WORK),'action':'diff'},record,str(WORK))['diff']=='ordinary file diff\n'
with patch.object(permissions,'git_repository',return_value=WORK),patch.object(permissions,'git',side_effect=lambda repo,*args:b'ordinary file diff\n' if args[0]=='diff' else git(repo,*args)),patch.object(permissions,'authorize'):
 # Staged gitlink changes remain inspectable even with a submodule in the index.
 assert git_tools.execute('git_read',{'path':str(WORK),'action':'diff','staged':True},record,str(WORK))['diff']=='ordinary file diff\n'
