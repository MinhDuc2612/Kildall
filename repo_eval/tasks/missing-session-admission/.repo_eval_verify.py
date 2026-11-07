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

db=WORK/'state.db';kildall.initialize(db)
with patch.object(kildall,'process_start',return_value='owner'),patch.object(threading.Thread,'start'):
 rejected(lambda:kildall.Task(db,'deleted-session'),(RuntimeError,PermissionError,ValueError))

with kildall.database(db) as con:con.execute("INSERT INTO orbi_sessions VALUES(?,?,?)",('kept',str(WORK),0))
with patch.object(kildall,'process_start',return_value='owner'),patch.object(threading.Thread,'start'):
 live=kildall.Task(db,'kept')
 assert live.session=='kept'

parent=dict(parent_task=live.id,parent_decision='decision',project=str(WORK),tools=[],requested=[],mode='shared')
with kildall.database(db) as con:con.execute('DELETE FROM orbi_sessions WHERE id=?',('kept',))
with patch.object(kildall,'process_start',return_value='owner'),patch.object(threading.Thread,'start'):
 rejected(lambda:kildall.Task(db,'kept',parent=parent),(RuntimeError,PermissionError,ValueError))
with kildall.database(db) as con:
 assert con.execute('SELECT count(*) FROM orbi_tasks').fetchone()[0]==1
