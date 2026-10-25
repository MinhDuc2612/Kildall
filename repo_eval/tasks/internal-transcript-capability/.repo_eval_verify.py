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

import subagents
db=WORK/'audit.db';kildall.initialize(db)
manager=object.__new__(subagents.Manager);manager.config={'paths':{'db_path':db}};manager.project=str(WORK);manager.memory=Mock();manager.hooks=None;manager.parent=SimpleNamespace(path=db);manager.requested=()
child={'task':SimpleNamespace(id='child'),'memory':Mock(),'project':str(WORK)}
@contextlib.contextmanager
def decision(*a,**k):
 yield {'update':Mock(),'agent':{'project':str(WORK),'tools':'[]'},'task':'child'}
def execute(op,args,record,project):
 assert record.get('transcript_capability') is not True,'Model minted transcript capability'
with patch.object(permissions,'decision',side_effect=decision),patch.object(permissions,'execute',side_effect=execute):
 manager.action(child,'_agent_memory',{'text':'untrusted'})
