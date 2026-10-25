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

db=WORK/'audit.db';kildall.initialize(db)
with permissions.decision(db,str(WORK),'run_command',{}) as row:
 row['update'](status='background')
with kildall.database(db) as con:
 assert con.execute('SELECT status FROM orbi_permissions').fetchone()[0]=='background'
