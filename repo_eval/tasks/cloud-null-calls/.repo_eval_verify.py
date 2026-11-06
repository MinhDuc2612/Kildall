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

import cloud
r={'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'READY','tool_calls':None}}]}
assert cloud.validate_message(r,[])=={'role':'assistant','content':'READY'}

tool={'type':'function','function':{'name':'t','parameters':{'type':'object','properties':{},'required':[],'additionalProperties':False}}}
call={'id':'c1','type':'function','function':{'name':'t','arguments':'{}'}}
good={'choices':[{'finish_reason':'tool_calls','message':{'role':'assistant','content':'','tool_calls':[call]}}]}
assert cloud.validate_message(good,[tool])['tool_calls'][0]['function']['name']=='t'
bad={'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'x','tool_calls':'broken'}}]}
rejected(lambda:cloud.validate_message(bad,[]),ValueError)
