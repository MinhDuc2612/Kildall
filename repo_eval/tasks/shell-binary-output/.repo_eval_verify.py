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

import shell_tools, base64
with patch.object(shell_tools.system(),'sandbox_command',side_effect=lambda argv:argv):
 result=shell_tools.run_bounded(['/usr/bin/printf','%b',r'\377'],str(WORK),5)
assert result['exit_code']==0 and result['stdout'] is None
assert base64.b64decode(result['stdout_base64'])==bytes([255])
