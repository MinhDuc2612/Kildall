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
def hook(bundle,phase,operation,args,row,project):
 if phase=='after':raise RuntimeError('post hook failed')
with patch.object(hooks,'run_stage',side_effect=hook),patch.object(kildall,'process_start',return_value='owner'):
 try:
  with permissions.decision(db,str(WORK),'read',{},hooks={}) as row:
   row['update'](status='background')
 except RuntimeError:pass
with kildall.database(db) as db:
 assert db.execute('SELECT status FROM orbi_permissions').fetchone()[0]=='background'
