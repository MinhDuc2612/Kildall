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

import subagents as a
db=WORK/'state.db';kildall.initialize(db)
parent=SimpleNamespace(path=db,id='parent',session='session',set=Mock())
child=Mock(id='child',path=db);child.finished=threading.Event();child.finish.side_effect=lambda outcome:child.finished.set()
cfg={'paths':{'db_path':db},'runtime':{'port':8123,'parallel':3,'context_size':4096}}
manager=a.Manager(cfg,Mock(),parent,str(WORK),[])
record={'task':'parent','id':'decision','requested':set(),'update':Mock()}
with a.bind_slot(kildall.url(cfg),1,3),patch.object(a,'capacity',return_value={'separate_cap':0,'pressure':1,'available_bytes':10**12}),patch.object(kildall,'Task',return_value=child),patch.object(manager,'action'),patch.object(manager,'infer',return_value={'role':'assistant','content':'Finished'}),patch.object(a,'stop_jobs',return_value=[{'status':'cancelled'}]),patch.object(a,'wait_idle'):
 result=manager.spawn({'tasks':[{'prompt':'Complete work'}]},record)
assert result['results'][0]['error']
child.finish.assert_called_once_with('error')
