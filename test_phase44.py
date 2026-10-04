"""Child isolation/admission, the real executor, cancellation and crash recovery; no model."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import Mock, patch

import kildall
import permissions as p
import subagents as a
import tool_runtime
from tool_grammar import parse_tool_call, tool_grammar
from test_tool_grammar import call


def refused(fn):
    try:
        fn()
    except (PermissionError, ValueError):
        return
    raise AssertionError('Expected refusal')


def main():
    checks = []
    def passed(name):
        checks.append(name)
        print('PASS:', name, flush=True)
    with tempfile.TemporaryDirectory(dir=kildall.ROOT / '.session', prefix='phase44-test-') as temp:
        root = Path(temp)
        db_path = root / 'audit.db'
        project = str(root)
        kildall.initialize(db_path)
        with kildall.database(db_path) as db:
            db.execute('INSERT INTO orbi_sessions VALUES(?,?,?)', ('parent', project, time.time()))
        parent = kildall.Task(db_path, 'parent')
        parent.message(dict(role='user', content='PARENT PRIVATE HISTORY'))
        config = kildall.settings()
        config['runtime'] = dict(config['runtime'], port=18123, parallel=2)
        config['paths'] = dict(config['paths'], db_path=db_path)
        memory = Mock()
        memory.retrieve.return_value = dict(text='', items=[], truncated=False)
        memory.add.return_value = 42
        manager = a.Manager(config, memory, parent, project, kildall.BASE_TOOLS)
        target = root / 'note.txt'
        target.write_text('original')
        budget = dict(available_bytes=4*1024**3, reserve_bytes=a.RESERVE, pressure=1,
                      memory_cap=0, separate_cap=0, separate_certified=False)
        barrier = threading.Barrier(2)
        seen = []
        main_thread = threading.get_ident()
        confirmations = []
        def confirm(preview):
            assert threading.get_ident() == main_thread
            confirmations.append(preview)
            return True
        def infer(child, cancel):
            assert 'PARENT PRIVATE HISTORY' not in json.dumps(child['messages'])
            assert [t['function']['name'] for t in manager.tools] == [t['function']['name'] for t in kildall.BASE_TOOLS]
            assert len({c['task'].id for c in seen} | {child['task'].id}) <= 2
            if len(child['messages']) == 1:
                seen.append(child)
                barrier.wait(timeout=3)
                return dict(role='assistant', content='', tool_calls=[dict(id=child['task'].id, type='function',
                    function=dict(name='write', arguments=json.dumps(dict(path=str(root/(child['prompt']+'.txt')), content=child['prompt']))))])
            return dict(role='assistant', content='result '+child['prompt'])
        def spawn(spec):
            with p.decision(db_path, project, 'spawn_agents', spec, parent.id) as record:
                record['agent_capability'] = manager
                return p.execute('spawn_agents', spec, record, project)
        with a.turn_slot(config), patch.object(a, 'capacity', return_value=budget), \
             patch.object(manager, 'infer', side_effect=infer), patch.object(p, 'terminal_confirm', side_effect=confirm):
            result = spawn(dict(tasks=[dict(prompt='ALPHA'), dict(prompt='BETA')]))
        assert len(result['results']) == 2 and all(r['error'] is None for r in result['results']), result
        assert {r['text'] for r in result['results']} == {'result ALPHA','result BETA'}
        assert len(confirmations) == 2 and all(r['before'] == '' for r in confirmations), confirmations
        assert (root/'ALPHA.txt').read_text() == 'ALPHA' and (root/'BETA.txt').read_text() == 'BETA'
        assert len({c['task'].id for c in seen}) == 2
        passed('1/2/8: separate contexts overlap on one runtime, parent receives both results and owns confirmations')

        with kildall.database(db_path) as db:
            agents = [dict(r) for r in db.execute('SELECT * FROM orbi_agents')]
            permissions = [dict(r) for r in db.execute('SELECT * FROM orbi_permissions WHERE task IN (SELECT task FROM orbi_agents)')]
            links = dict(db.execute('SELECT id,parent FROM orbi_permission_parents'))
        assert all(links[r['id']] in {c['parent_decision'] for c in agents} for r in permissions)
        assert all(r['status']=='done' for r in permissions)
        assert all(c['project']==project and c['parent_task']==parent.id for c in agents)
        assert all(c.kwargs['scope']=='project' and c.kwargs['project']==project for c in memory.add.call_args_list)
        assert not kildall.history(db_path,'parent')  # Only the still-active parent; completed children are excluded.
        passed('Every child action has a parent decision; child transcripts cannot enter parent history or global memory')

        child = seen[0]
        writes = memory.add.call_count
        refused(lambda: manager.action(child, '_agent_memory', dict(text='forged internal transcript')))
        assert memory.add.call_count == writes
        passed('Model-selected internal action names cannot acquire transcript capabilities')
        def action(name, args, **extra):
            with p.decision(db_path, extra.get('project', project), name, args, child['task'].id,
                            requested=('commit','push'), hooks=extra.get('hooks')) as record:
                record['memory_capability'] = memory
                record['agent_capability'] = manager
                return p.execute(name, args, record, extra.get('project',project))
        with patch.object(kildall, 'SYSTEM_RULES', ''):
            for name,args in [('spawn_agents',dict(tasks=[dict(prompt='recurse')])),
                              ('run_command',dict(command='rm -rf '+project)),
                              ('run_command',dict(command='sudo true')),
                              ('run_command',dict(command='screencapture image.png')),
                              ('git_push',dict(path=project,branch='main')),
                              ('remember',dict(text='leak',scope='global',tier='L1')),
                              ('write',dict(path=str(root.parent.parent.parent/'escape.txt'),content='no'))]:
                refused(lambda: action(name,args))
        refused(lambda: action('remember',dict(text='leak',scope='project',tier='L1'),project=str(root.parent)))
        refused(lambda: kildall.Task(db_path, 'parent', parent=dict(parent_task=child['task'].id)))
        (root/'hooks.toml').write_text('')
        import hooks
        refused(lambda: action('spawn_agents',dict(tasks=[dict(prompt='recurse')]),hooks=hooks.load(root/'hooks.toml')))
        assert len(kildall.BASE_TOOLS)==12 and 'spawn_agents' not in [t['function']['name'] for t in kildall.TOOLS]
        grammar = tool_grammar([*kildall.BASE_TOOLS,a.TOOL])
        assert grammar and parse_tool_call(call('spawn_agents',dict(tasks=[dict(prompt='x')])),[a.TOOL])['name']=='spawn_agents'
        passed('9: prompt-free recursion, tool escalation, global-memory writes, Never commands and computer use refused; strict GBNF')

        with a.turn_slot(config), patch.object(a,'capacity',return_value=budget):
            refused(lambda: spawn(dict(tasks=[dict(prompt='x',mode='separate')])))
            manager.mode='separate'
            refused(lambda: spawn(dict(tasks=[dict(prompt='x',mode='separate')])))
            refused(lambda: spawn(dict(tasks=[dict(prompt='x')]*3)))
            with patch.object(a,'capacity',return_value=dict(budget,pressure=4)):
                refused(lambda: spawn(dict(tasks=[dict(prompt='x')])))
            with patch.object(a,'capacity',return_value=dict(budget,available_bytes=a.SLOT_RSS-1)):
                refused(lambda: spawn(dict(tasks=[dict(prompt='x')])))
        passed('3/4/7: separate mode requires opt-in but measured cap0 refuses it; slot, RAM and critical-pressure admission fail closed')

        # Exercise the dormant launch/cleanup branch with admission and model startup
        # substituted. This is a lifecycle test, not a successful hardware measurement.
        launched=[]
        def separate_start(config, **kwargs):
            assert kwargs==dict(lane_only=True)
            assert config['runtime']['parallel']==1 and config['runtime']['context_size']==4096
            assert config['runtime']['port']!=manager.config['runtime']['port']
            assert config['lanes']['a']['model']==manager.config['lanes']['a']['model']
            launched.append(config['paths']['code_dir'])
        with a.turn_slot(config),patch.object(a,'capacity',return_value=dict(budget,separate_cap=1)), \
             patch.object(kildall,'ensure_runtime',side_effect=separate_start), \
             patch.object(manager,'infer',return_value=dict(role='assistant',content='separate result')):
            result=spawn(dict(tasks=[dict(prompt='separate test',mode='separate')]))
        assert len(launched)==1 and result['results'][0]['error'] is None
        launched[0].rmdir()
        passed('Separate launch branch uses its own fixed-model server and cleanup; simulated admission only, real hardware cap remains0')

        (root/'feedback.sh').write_text("printf '%s\\n' 'untrusted child hook data'\n")
        (root/'feedback.toml').write_text('before=["feedback.sh"]\n')
        manager.hooks=hooks.load(root/'feedback.toml')
        with a.turn_slot(config),patch.object(a,'capacity',return_value=budget), \
             patch.object(manager,'infer',return_value=dict(role='assistant',content='hook child')):
            feedback=spawn(dict(tasks=[dict(prompt='hook child')]))
        assert 'untrusted child hook data' in json.dumps(feedback['results'][0]['hook_feedback'])
        manager.hooks=None
        passed('Automatic child-memory hook feedback also reaches the parent as tool data')

        action('run_command',dict(command='cd ..'))
        assert action('run_command',dict(command='pwd'))['cwd']==str(root.parent)
        with p.decision(db_path,project,'run_command',{},parent.id) as record:
            assert p.execute('run_command',dict(command='pwd'),record,project)['cwd']==project
        background = action('run_command',dict(command='sleep 20',background=True))
        other=seen[1]
        with p.decision(db_path,project,'shell_job',{},other['task'].id) as record:
            refused(lambda:p.execute('shell_job',dict(id=background['id']),record,project))
        a.stop_jobs(db_path,child['task'].id)
        result = action('shell_job',dict(id=background['id']))
        assert result['result']['cancelled']
        passed('Child cwd and background-job access isolated; cancellation reaps a real child shell worker')

        replies=[dict(role='assistant',content='',tool_calls=[dict(id='background',type='function',
            function=dict(name='run_command',arguments=json.dumps(dict(command='sleep 20',background=True))))]),
            dict(role='assistant',content='Background job launched')]
        with a.turn_slot(config),patch.object(a,'capacity',return_value=budget),patch.object(manager,'infer',side_effect=replies):
            result=spawn(dict(tasks=[dict(prompt='start a background job')]))['results'][0]
        assert result['error'] and len(result['cancelled_jobs'])==1,result
        assert result['cancelled_jobs'][0]['result']['cancelled']
        with kildall.database(db_path) as db:
            assert db.execute('SELECT outcome FROM orbi_tasks WHERE id=?',(result['id'],)).fetchone()[0]=='error'
        passed('Normal batch cleanup reports cancelled background jobs and cannot mark the child successful')

        with a.bind_slot(kildall.url(config),1,2):
            assert a.inference_body(kildall.url(config)+'/completion',{})['id_slot']==1
            assert a.inference_body(kildall.url(config)+'/v1/chat/completions',{})['id_slot']==1
            refused(lambda:a.inference_body(kildall.url(config)+'/completion',dict(id_slot=3)))
        refused(lambda:a.inference_body(kildall.url(config)+'/completion',dict(id_slot=0)))
        with a.lease(config,1):
            @contextmanager
            def second():
                with a.lease(config,1,blocking=False):yield
            refused(lambda:second().__enter__())
        passed('5: validated slot identity and cross-process locking prevent busy pinned-slot reuse; runtime allocation tested live separately')
        with patch.object(kildall,'json_request',side_effect=[
                [dict(id=0,n_ctx=4096,is_processing=True)],
                [dict(id=0,n_ctx=4096,is_processing=False)]]) as slots:
            a.wait_idle(config,0)
            assert slots.call_count==2
        with patch.object(kildall,'json_request',return_value=[dict(id=0,n_ctx=1024,is_processing=False)]):
            try:a.wait_idle(config,0)
            except RuntimeError:pass
            else:raise AssertionError('Undersized slot accepted')
        passed('Slot handoff waits for server-side cancellation and refuses undersized contexts')

        connected=threading.Event()
        release=threading.Event()
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
                self.wfile.write(b'data: {"content":"hello","stop":false}\n\n');self.wfile.flush()
                connected.set();release.wait(5)
            def log_message(self,*args):pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        cancel=a.Cancellation();errors=[]
        def request():
            try:
                with patch.object(tool_runtime,'prepare',return_value=dict(stream=True)):
                    tool_runtime.chat(f'http://127.0.0.1:{server.server_port}',{},cancel=cancel)
            except Exception as error:errors.append(error)
        worker=threading.Thread(target=request);worker.start()
        assert connected.wait(3)
        started=time.monotonic();cancel.cancel();worker.join(2)
        release.set();server.shutdown();server.server_close();thread.join()
        assert not worker.is_alive() and errors and time.monotonic()-started<3
        passed('Ctrl-C cancellation transport interrupts an actual blocked HTTP stream and returns no partial tool call')

        for stage in ('fit-template', 'fit-tokenize', 'tool-template'):
            connected=threading.Event();release=threading.Event();errors=[];templates=[]
            class PreflightHandler(BaseHTTPRequestHandler):
                def do_POST(self):
                    self.rfile.read(int(self.headers['Content-Length']))
                    if self.path=='/apply-template':templates.append(self.path)
                    stalled=((stage=='fit-template' and self.path=='/apply-template') or
                             (stage=='fit-tokenize' and self.path=='/tokenize') or
                             (stage=='tool-template' and len(templates)==2))
                    self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
                    if stalled:
                        self.wfile.write(b'{');self.wfile.flush();connected.set();release.wait(5)
                    else:
                        self.wfile.write(json.dumps(dict(prompt='<|turn>user\nhello',tokens=[1])).encode())
                def log_message(self,*args):pass
            server=ThreadingHTTPServer(('127.0.0.1',0),PreflightHandler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            cancel=a.Cancellation()
            probe=dict(config=dict(config,runtime=dict(config['runtime'],port=server.server_port)),
                       task=Mock(),slot=0,memory='',messages=[dict(role='user',content='hello')],timings=[])
            def preflight():
                try:manager.infer(probe,cancel)
                except Exception as error:errors.append(error)
            worker=threading.Thread(target=preflight);worker.start()
            try:
                assert connected.wait(3),stage
                started=time.monotonic();cancel.cancel();worker.join(2)
                assert not worker.is_alive() and errors and time.monotonic()-started<3,stage
            finally:
                release.set();server.shutdown();server.server_close();thread.join();worker.join(6)
        passed('Child template, tokenization and tool-template preflights use the same cancellable transport')

        ready=threading.Event()
        def blocked(child,cancel):
            ready.set()
            cancel.stopped.wait(5)
            cancel.check()
            raise AssertionError('Cancellation was not delivered')
        def interrupt():
            if ready.wait(3):os.kill(os.getpid(),signal.SIGINT)
        interrupter=threading.Thread(target=interrupt);interrupter.start()
        with a.turn_slot(config),patch.object(a,'capacity',return_value=budget),patch.object(manager,'infer',side_effect=blocked):
            try:spawn(dict(tasks=[dict(prompt='cancel')]))
            except KeyboardInterrupt:pass
            else:raise AssertionError('SIGINT did not cancel the batch')
        interrupter.join()
        with kildall.database(db_path) as db:
            assert db.execute("SELECT count(*) FROM orbi_tasks WHERE id IN (SELECT task FROM orbi_agents) AND outcome IS NULL").fetchone()[0]==0
            assert db.execute("SELECT count(*) FROM orbi_permissions WHERE operation='spawn_agents' AND status='cancelled'").fetchone()[0]==1
        passed('Real SIGINT cancels the batch, joins inference workers and records terminal child/audit outcomes')

        # A separate OS process crashes after leaving one linked child and a live shell job.
        script=root/'crash.py'
        script.write_text('''import os,sys,time,json
from pathlib import Path
import kildall,permissions
p=Path(sys.argv[1]);kildall.initialize(p)
with kildall.database(p) as db:db.execute('INSERT INTO orbi_sessions VALUES(?,?,?)',('crash',sys.argv[2],time.time()))
parent=kildall.Task(p,'crash')
with permissions.decision(p,sys.argv[2],'spawn_agents',{},parent.id) as rec:
 child=kildall.Task(p,'crash',parent=dict(parent_task=parent.id,parent_decision=rec['id'],project=sys.argv[2],tools=['run_command'],requested=[],mode='shared'))
 with permissions.decision(p,sys.argv[2],'run_command',{},child.id) as action:
  result=permissions.execute('run_command',dict(command='sleep 30',background=True),action,sys.argv[2])
 Path(sys.argv[3]).write_text(json.dumps(dict(parent=parent.id,child=child.id,job=result['id'])))
 os._exit(19)
''')
        env=dict(os.environ,PYTHONPATH=str(kildall.ROOT))
        proc=subprocess.run([sys.executable,str(script),str(db_path),project,str(root/'crashed.json')],env=env,capture_output=True,text=True,timeout=10)
        assert proc.returncode==19,proc.stderr
        crashed=json.loads((root/'crashed.json').read_text())
        kildall.initialize(db_path)
        with kildall.database(db_path) as db:
            assert db.execute('SELECT outcome FROM orbi_tasks WHERE id=?',(crashed['child'],)).fetchone()[0]=='crashed'
            job=db.execute('SELECT result FROM orbi_shell_jobs WHERE id=?',(crashed['job'],)).fetchone()[0]
            assert json.loads(job)['cancelled']
        passed('Crash recovery marks child tasks and reaps unfinished child shell jobs without changing ordinary background-job semantics')
        parent.finish('done')
    print(json.dumps(dict(passed=True,checks=checks)))


if __name__=='__main__':main()
