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

import git_tools
p=WORK/'remote';(p/'objects').mkdir(parents=True);(p/'HEAD').write_text('ref: refs/heads/main\n');(p/'config').write_text('[core]\n bare=true\n precomposeunicode=true\n')
with patch.object(permissions,'git',return_value=(str(p)+'\n').encode()):
 assert git_tools.origin(WORK)[0]==str(p)

(p/'config').write_text('[core]\n bare=true\n sshcommand=evil\n')
with patch.object(permissions,'git',return_value=(str(p)+'\n').encode()):
 rejected(lambda:git_tools.origin(WORK),PermissionError)


for text in ('[core]\n bare=true\n hookspath=/tmp/x\n','[core]\n bare=true\n fsmonitor=x\n','[core]\n bare=true\n[receive]\n denyCurrentBranch=ignore\n'):
 (p/'config').write_text(text)
 with patch.object(permissions,'git',return_value=(str(p)+'\n').encode()):
  rejected(lambda:git_tools.origin(WORK),PermissionError)
