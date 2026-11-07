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
t=kildall.Task.__new__(kildall.Task);t.path=db;t.id='gone';t.session='s';t.lock=threading.RLock();t.state='idle';t.tty=False;t.finished=threading.Event();t.watcher=Mock()
rejected(lambda:t.set('waiting'),RuntimeError)

with kildall.database(db) as con:con.execute("INSERT INTO orbi_sessions VALUES(?,?,?)",('kept',str(WORK),0))
with patch.object(kildall,'process_start',return_value='owner'),patch.object(threading.Thread,'start'):
 live=kildall.Task(db,'kept')
live.set('waiting')
assert live.state=='waiting'
with kildall.database(db) as con:
 assert con.execute('SELECT state FROM orbi_tasks WHERE id=?',(live.id,)).fetchone()[0]=='waiting'
