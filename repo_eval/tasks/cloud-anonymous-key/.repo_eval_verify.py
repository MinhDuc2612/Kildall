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

import cloud, cloud_keys
cfg={'paths':{'db_path':WORK/'x.db'},'cloud':{'enabled':True,'providers':{'llm7':{'base_url':'https://api.llm7.io/v1','key_name':'LLM7_API_KEY','keyless':True,'allowed_models':['codestral-latest'],'context_tokens':32000,'limits_status':'unverified','trains_on_data':'unknown'}}}}
c=cloud.Client(cfg)
class Reply(io.BytesIO):
 status=200;headers={}
 def __init__(self):super().__init__(json.dumps({'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'READY'}}]}).encode())
with patch.object(cloud_keys,'get_key',return_value=None),patch.object(c.opener,'open',return_value=Reply()):
 assert c.reply([],[])['content']=='READY'
