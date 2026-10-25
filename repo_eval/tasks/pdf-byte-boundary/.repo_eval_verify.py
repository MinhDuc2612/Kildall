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

import file_tools
p=WORK/'a.pdf';p.write_bytes(b'%PDF')
capture={'exit_code':0,'timed_out':False,'stdout':None,'stderr':'','stdout_base64':'4oI=','truncated':True}
with patch.object(file_tools,'run_bounded',return_value=capture):
 r=file_tools.execute('read_pdf',{'path':str(p)},str(WORK))
assert r['encoding']=='base64' and r['data']=='4oI=' and r['truncated']
