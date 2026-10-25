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

import shell_tools
db=WORK/'jobs.db';kildall.initialize(db)
with kildall.database(db) as con:
 shell_tools.tables(con)
 con.execute("INSERT INTO orbi_permissions(id,project,operation,arguments,tier,status,pid,owner_start,created,updated) VALUES('job',?,'run_command','{}','Auto','background',123,'owner',0,0)",(str(WORK),))
 con.execute("INSERT INTO orbi_shell_jobs(id,project,cwd,command,timeout) VALUES('job',?,?,'true',30)",(str(WORK),str(WORK)))
complete={'stdout':'done','stderr':'','exit_code':0,'timed_out':False,'truncated':False}
def completed(pid):
 shell_tools.finish(db,'job',complete)
 return None
record={'id':'poll','db_path':db,'update':Mock()}
with patch.object(kildall,'process_start',side_effect=completed),patch.object(shell_tools,'stop_owned_child'):
 result=shell_tools.execute('shell_job',{'id':'job'},record,str(WORK))
assert result['status']=='done' and result['result']==complete
