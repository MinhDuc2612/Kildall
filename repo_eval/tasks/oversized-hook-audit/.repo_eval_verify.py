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

import hooks
db=WORK/'audit.db';kildall.initialize(db)
record={'db_path':db,'task':None,'id':'parent','status':'done','result':'x'*70000}
bundle={'after':[('script','true')],'timeout':1}
rejected(lambda:hooks.run_stage(bundle,'after','read',{},record,str(WORK)),hooks.HookFailure)
with kildall.database(db) as con:
 rows=con.execute("SELECT operation,status FROM orbi_permissions").fetchall()
assert len(rows)==1 and rows[0]['operation']=='_hook' and rows[0]['status']=='failed'

small=dict(record,id='small',result='x');small.pop('hook_feedback',None)
fine=dict(exit_code=0,timed_out=False,truncated=False,stdout='',stderr='')
with patch.object(hooks,'shell',return_value=fine):
 hooks.run_stage(bundle,'after','read',{},small,str(WORK))
with kildall.database(db) as con:
 assert con.execute("SELECT count(*) FROM orbi_permissions WHERE operation='_hook' AND status='done'").fetchone()[0]==1
