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

import router_warmth as warmth
with patch.object(kildall,'json_request',return_value={'tokens_evaluated':2,'timings':{}}):
 rejected(lambda:warmth.warm({'runtime':{'port':8123}},[1,2,3]),(ValueError,RuntimeError))

with patch.object(kildall,'json_request',return_value={'tokens_evaluated':3,'timings':{'prompt_n':3}}):
 assert warmth.warm({'runtime':{'port':8123}},[1,2,3])['timings']=={'prompt_n':3}


with patch.object(kildall,'json_request',return_value={'timings':{}}):
 rejected(lambda:warmth.warm({'runtime':{'port':8123}},[1,2,3]),(ValueError,RuntimeError))
import subagents
class Stream(list):
 def __enter__(self):return self
 def __exit__(self,*a):return False
class Cancel:
 def open(self,request,timeout):return Stream([b'data: '+json.dumps({'stop':True,'tokens_evaluated':2,'timings':{}}).encode()+b'\n'])
 def check(self):pass
with patch.object(subagents,'inference_body',side_effect=lambda endpoint,body:body):
 rejected(lambda:warmth.warm({'runtime':{'port':8123}},[1,2,3],cancel=Cancel()),(ValueError,RuntimeError))

class Complete(Cancel):
 def open(self,request,timeout):return Stream([b'data: '+json.dumps({'stop':True,'tokens_evaluated':3,'timings':{'prompt_n':3}}).encode()+b'\n'])
with patch.object(subagents,'inference_body',side_effect=lambda endpoint,body:body):
 assert warmth.warm({'runtime':{'port':8123}},[1,2,3],cancel=Complete())['timings']=={'prompt_n':3}
