"""Bounded child contexts; only inference runs concurrently, tools stay with the parent."""
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import contextmanager, ExitStack
from contextvars import ContextVar
import fcntl
import copy
import errno
import http.client
import json
import os
from pathlib import Path
import re
import signal
import socket
import subprocess
import threading
import time
from urllib.parse import urlsplit
from urllib.error import URLError

from shell_tools import tool

TOOL = tool('spawn_agents', 'Run independent child tasks and return their results. Children cannot delegate. Shared mode uses the resident model; separate mode needs explicit user opt-in and measured RAM capacity.',
    dict(tasks=dict(type='array', minItems=1, maxItems=2, items=dict(type='object',
        properties=dict(prompt=dict(type='string'), mode=dict(type='string', enum=['shared', 'separate'])),
        required=['prompt'], additionalProperties=False))), ['tasks'])

# Measured on this 24GiB M4, b10809/IQ3; see BENCHMARKS and phase4.4 sizing.json.
RESERVE = 2 * 1024**3
SLOT_RSS = 533315584
PROCESS_RSS = 11635621888
SEPARATE_CERTIFIED = False  # Real dual-model generation failed with Metal OOM.
_SLOT = ContextVar('kildall_slot', default=None)


def capacity():
    text = subprocess.check_output(['vm_stat'], text=True, timeout=5)
    page = int(re.search(r'page size of (\d+)', text)[1])
    pages = {k: int(v) for k, v in re.findall(r'^([^:\n]+):\s+(\d+)\.', text, re.M)}
    available = page * sum(pages[k] for k in ('Pages free', 'Pages inactive', 'Pages speculative'))
    pressure = int(subprocess.check_output(['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True, timeout=5))
    budget = max(0, available - RESERVE) if pressure != 4 else 0
    memory_cap = budget // PROCESS_RSS
    return dict(available_bytes=available, reserve_bytes=RESERVE, pressure=pressure,
                extra_process_rss_bytes=PROCESS_RSS, memory_cap=memory_cap,
                separate_cap=memory_cap if SEPARATE_CERTIFIED else 0,
                separate_certified=SEPARATE_CERTIFIED)


@contextmanager
def bind_slot(endpoint, slot, count):
    if type(slot) is not int or type(count) is not int or not 0 <= slot < count <= 3:
        raise ValueError('Invalid measured slot id/count')
    token = _SLOT.set((endpoint, slot, count))
    try:
        yield
    finally:
        _SLOT.reset(token)


def inference_body(endpoint, body):
    selected = _SLOT.get()
    if selected and endpoint.removesuffix('/v1/chat/completions').removesuffix('/completion') == selected[0]:
        if 'id_slot' in body and body['id_slot'] != selected[1]:
            raise ValueError('Request attempted to change its owned slot')
        return dict(body, id_slot=selected[1])
    raise ValueError('Inference requires validated slot ownership')


def work_slots(config):
    count = config['runtime'].get('parallel', 1)
    return tuple(range(1, count)) if count > 1 else (0,)


@contextmanager
def request_slot(endpoint):
    """Direct generation clients borrow work capacity, never the router slot."""
    from kildall import settings, url
    endpoint = endpoint.removesuffix('/v1/chat/completions').removesuffix('/completion')
    from router_warmth import foreground
    with foreground(endpoint):
        selected = _SLOT.get()
        if selected and selected[0] == endpoint:
            yield
            return
        config = settings()
        if endpoint != url(config):
            raise ValueError('Unbound inference must use the configured local runtime')
        with turn_slot(config):
            yield


@contextmanager
def router_slot(config):
    if 'runtime' not in config:
        yield
        return
    from kildall import url
    count = config['runtime'].get('parallel', 1)
    if _SLOT.get() == (url(config), 0, count):
        yield  # The one-slot recall/control configuration already owns slot0.
        return
    with lease(config, 0), bind_slot(url(config), 0, count):
        yield


def wait_idle(config, slot, *, cancel=None):
    """A disconnected client may end before llama.cpp has processed its cancellation."""
    from kildall import json_request, url
    deadline = time.monotonic() + 30
    while True:
        if cancel is not None:
            cancel.check()
        try:
            rows = json_request(url(config) + '/slots', timeout=1, cancel=cancel)
        except URLError as error:
            if getattr(error.reason, 'errno', None) == errno.ECONNREFUSED:
                return  # Cold start; ensure_runtime will establish ownership.
            raise
        matches = [row for row in rows if row['id'] == slot]
        if len(matches) != 1 or matches[0].get('n_ctx', 0) < 4096:
            raise RuntimeError('Runtime slot does not have its full 4096-token context')
        if not matches[0]['is_processing']:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError('Previous slot request has not drained; refusing pinned-slot reuse')
        time.sleep(.05)


@contextmanager
def lease(config, slot, *, blocking=True, cancel=None):
    from kildall import ROOT, url
    from router_warmth import foreground
    count = config['runtime'].get('parallel', 1)
    if type(slot) is not int or not 0 <= slot < count <= 3:
        raise ValueError('Slot exceeds measured capacity')
    directory = ROOT / '.session'
    directory.mkdir(exist_ok=True)
    with foreground(url(config)), (directory / f"slot-{config['runtime']['port']}-{slot}.lock").open('a') as lock:
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if not blocking:
                    raise PermissionError('Shared slot is owned by another task')
                time.sleep(.05)
        try:
            wait_idle(config, slot, **({'cancel': cancel} if cancel is not None else {}))
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


@contextmanager
def turn_slot(config):
    # Small unit controls supply no runtime; no transport exists in that case.
    if 'runtime' not in config:
        yield
        return
    from kildall import url
    # ponytail: turns share the first work slot; children borrow it while the
    # parent waits. Wider work admission requires a measured configuration.
    slot = work_slots(config)[0]
    with lease(config, slot), bind_slot(url(config), slot, config['runtime'].get('parallel', 1)):
        yield


class Cancellation:
    def __init__(self):
        self.stopped = threading.Event()
        self.lock = threading.Lock()
        self.connections = {}

    def check(self):
        if self.stopped.is_set():
            raise InterruptedError('Child inference cancelled')

    @contextmanager
    def open(self, request, timeout):
        target = urlsplit(request.full_url)
        if target.scheme != 'http' or target.hostname != '127.0.0.1':
            raise ValueError('Child inference requires the local runtime')
        conn = http.client.HTTPConnection(target.hostname, target.port, timeout=timeout)
        with self.lock:
            self.check()
            self.connections[conn] = None
        try:
            conn.connect()
            with self.lock:
                self.connections[conn] = conn.sock
                self.check()
            conn.request(request.get_method(), target.path, request.data, {'Content-Type': 'application/json'})
            with conn.getresponse() as response:
                if response.status != 200:
                    raise RuntimeError(f'Child inference HTTP {response.status}: {response.read(4096)!r}')
                yield response
        finally:
            with self.lock:
                self.connections.pop(conn, None)
            conn.close()

    def cancel(self):
        with self.lock:
            self.stopped.set()
            for sock in self.connections.values():
                if sock is not None:
                    try:
                        sock.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass


def stop_jobs(path, task):
    from kildall import database, process_start, owns_server, atomic_json
    from shell_tools import stop_owned_child
    with database(path) as db:
        foreground = db.execute('SELECT * FROM orbi_agent_processes WHERE task=?', (task,)).fetchall()
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        jobs = db.execute('SELECT p.id,p.pid,p.owner_start FROM orbi_permissions p JOIN orbi_shell_jobs j ON j.id=p.id '
                          'WHERE p.task=? AND j.result IS NULL', (task,)).fetchall() if 'orbi_shell_jobs' in tables else []
        runtime = db.execute('SELECT directory FROM orbi_agent_runtimes WHERE task=?', (task,)).fetchone()
    if runtime is not None:
        state_file = Path(runtime['directory']) / '.session/services.json'
        if state_file.is_file():
            state = json.loads(state_file.read_text())
            for server in state.values():
                if owns_server(server):
                    os.kill(server['pid'], signal.SIGINT)
                    deadline = time.monotonic() + 20
                    while owns_server(server) and time.monotonic() < deadline:
                        time.sleep(.1)
                    if owns_server(server):
                        stop_owned_child(server['pid'], server['started'])
                        if owns_server(server):
                            raise RuntimeError('Child runtime did not stop')
            atomic_json(state_file, {})
        with database(path) as db:
            db.execute('DELETE FROM orbi_agent_runtimes WHERE task=?', (task,))
    for row in foreground:
        stop_owned_child(row['pid'], row['started'])
    with database(path) as db:
        db.execute('DELETE FROM orbi_agent_processes WHERE task=?', (task,))
    cancelled = []
    for row in jobs:
        if process_start(row['pid']) == row['owner_start'] and row['pid'] != os.getpid():
            try:
                os.kill(row['pid'], signal.SIGTERM)
            except ProcessLookupError:
                pass
            deadline = time.monotonic() + 2
            while process_start(row['pid']) == row['owner_start'] and time.monotonic() < deadline:
                time.sleep(.05)
            stop_owned_child(row['pid'], row['owner_start'])
        with database(path) as db:
            current = db.execute('SELECT * FROM orbi_shell_jobs WHERE id=?', (row['id'],)).fetchone()
        stop_owned_child(current['child_pid'], current['child_start'])
        if current['result'] is None:
            from shell_tools import finish
            finish(path, row['id'], dict(stdout='', stderr='Agent owner ended', exit_code=None,
                timed_out=False, truncated=False, cancelled=True))
        with database(path) as db:
            result = json.loads(db.execute('SELECT result FROM orbi_shell_jobs WHERE id=?', (row['id'],)).fetchone()[0])
        if result.get('cancelled'):
            cancelled.append(dict(id=row['id'], result=result))
    return cancelled


def recover(path):
    from kildall import database, process_start
    with database(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS orbi_agent_processes(permission TEXT PRIMARY KEY, task TEXT NOT NULL, pid INTEGER NOT NULL, started TEXT NOT NULL)')
        rows = db.execute('SELECT a.task,t.pid,t.owner_start,t.outcome FROM orbi_agents a '
                          'JOIN orbi_tasks t ON t.id=a.parent_task WHERE a.result IS NULL').fetchall()
    for row in rows:
        if row['outcome'] is not None or process_start(row['pid']) != row['owner_start']:
            stop_jobs(path, row['task'])
            with database(path) as db:
                db.execute('UPDATE orbi_agents SET result=? WHERE task=? AND result IS NULL',
                           (json.dumps(dict(error='Parent ended before collecting child result; inspect transcript')), row['task']))


class Manager:
    def __init__(self, config, memory, parent, project, tools, requested=(), hooks=None, mode='shared'):
        if mode not in ('shared', 'separate'):
            raise ValueError('Unknown agent mode')
        self.config, self.memory, self.parent, self.project = config, memory, parent, project
        self.tools = [t for t in tools if t['function']['name'] != 'spawn_agents']
        self.requested, self.hooks, self.mode = tuple(requested), hooks, mode
        self.max_tokens = 512

    def action(self, child, operation, args, *, automatic=False):
        from permissions import decision, execute
        from hooks import feedback_result
        with decision(self.parent.path, self.project, operation, args, child['task'].id,
                      requested=self.requested, hooks=self.hooks) as record:
            record['memory_capability'] = self.memory
            if automatic and operation == '_agent_memory':
                record['transcript_capability'] = True
            result = execute(operation, args, record, self.project)
            if 'memory_text' in record:
                child['memory'] = record['memory_text']
            record['result'] = result
        result = feedback_result(result, record)
        if automatic and record.get('hook_feedback'):
            child.setdefault('automatic_feedback', []).append(result)
        return result

    def infer(self, child, cancel):
        import kildall
        from tool_runtime import chat
        task = child['task']
        config = child['config']
        with bind_slot(kildall.url(config), child['slot'], config['runtime'].get('parallel', 1)):
            wait_idle(config, child['slot'], cancel=cancel)
            messages = kildall.fit_messages(config, kildall.system_prompt(self.project), child['memory'], [], child['messages'], tools=self.tools, cancel=cancel)
            partial = dict(role='assistant', content='')
            ident = task.message(partial)
            last = time.monotonic()
            def content(text):
                nonlocal last
                partial['content'] += text
                task.set('thinking')
                if time.monotonic() - last > .1:
                    task.message(partial, ident)
                    last = time.monotonic()
            try:
                started = time.perf_counter()
                response = chat(kildall.url(config), dict(messages=messages, tools=self.tools,
                    tool_choice='auto', parallel_tool_calls=False, temperature=0, top_p=1, samplers=['temperature'], seed=42,
                    max_tokens=self.max_tokens, stream=True, cache_prompt=False), on_text=content, cancel=cancel)
                partial.update(response['choices'][0]['message'])
                child['timings'].append(dict(wall_s=time.perf_counter()-started, **response['timings']))
                return partial
            finally:
                task.message(partial, ident)

    def spawn(self, args, record):
        import kildall
        from permissions import authorize, decision
        from tool_grammar import validate_arguments
        from tool_validation import copy_issues, retry_feedback
        from hooks import HookFailure
        validate_arguments(TOOL['function']['parameters'], args)
        if record['task'] != self.parent.id or record.get('agent'):
            raise PermissionError('A subagent cannot spawn a subagent')
        budget = capacity()
        record['update'](preview=dict(capacity=budget, tasks=args['tasks']))
        separate = sum(t.get('mode', 'shared') == 'separate' for t in args['tasks'])
        if separate:
            if self.mode != 'separate':
                raise PermissionError('Separate mode requires explicit --agents separate')
            if separate > budget['separate_cap']:
                raise PermissionError(f"Separate-process cap is {budget['separate_cap']}: dual-model Metal OOM; remeasurement required")
        count = self.config['runtime'].get('parallel', 1)
        shared = len(args['tasks']) - separate
        work = work_slots(self.config)
        active_shared = min(shared, len(work))
        # Shared KV is already allocated by the resident server. Budget observed
        # per-slot overhead for active children; the new-model reserve above is
        # for separate-process admission, not a second reservation of resident KV.
        if budget['pressure'] == 4 or budget['available_bytes'] < (active_shared + separate) * SLOT_RSS:
            raise PermissionError('Measured shared slot/RAM capacity would be exceeded')
        if any(not t['prompt'].strip() or len(t['prompt']) > 65536 for t in args['tasks']):
            raise ValueError('Expected nonempty bounded child prompts')
        selected = _SLOT.get()
        if selected != (kildall.url(self.config), work[0], count):
            raise PermissionError('Child tasks require the parent slot lease')
        children, pending = [], {}
        cancel = Cancellation()
        with ExitStack() as leases:
            if separate:
                # ponytail: one admitted separate batch at a time across parents;
                # a measured reservation ledger is needed for concurrent batches.
                lock = leases.enter_context((kildall.ROOT / '.session/separate.lock').open('a'))
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as error:
                    raise PermissionError('Another parent owns separate-process admission') from error
                if separate > capacity()['separate_cap']:
                    raise PermissionError('Separate-process RAM capacity changed before admission')
            for slot in work[1:active_shared]:
                leases.enter_context(lease(self.config, slot, blocking=False))
            authorize(record, 'Auto')
            pool = ThreadPoolExecutor(max_workers=active_shared + separate, thread_name_prefix='kildall-child')
            try:
                shared_slot = 0
                for spec in args['tasks']:
                    mode = spec.get('mode', 'shared')
                    task = kildall.Task(self.parent.path, self.parent.session, parent=dict(parent_task=self.parent.id,
                        parent_decision=record['id'], project=self.project, tools=[t['function']['name'] for t in self.tools],
                        requested=self.requested, mode=mode))
                    child = dict(task=task, slot=work[shared_slot % len(work)] if mode == 'shared' else 0, config=self.config,
                                 prompt=spec['prompt'], memory='', messages=[dict(role='user', content=spec['prompt'])],
                                 answer=[], turns=0, retry=False, pending_copy=False, stopped=False, timings=[])
                    children.append(child)
                    if mode == 'separate':
                        config = copy.deepcopy(self.config)
                        config['paths']['code_dir'] = kildall.ROOT / '.session' / ('agent-runtime-' + task.id)
                        config['paths']['code_dir'].mkdir()
                        with socket.socket() as probe:
                            probe.bind(('127.0.0.1', 0))
                            config['runtime']['port'] = probe.getsockname()[1]
                        config['runtime']['parallel'] = 1
                        child['config'] = config
                        with kildall.database(task.path) as db:
                            db.execute('INSERT INTO orbi_agent_runtimes VALUES(?,?)', (task.id, str(config['paths']['code_dir'])))
                        # The parent is the only process that may create this fixed
                        # model server. No executable/path comes from a tool argument.
                        kildall.ensure_runtime(config, lane_only=True)
                    else:
                        shared_slot += 1
                    task.message(child['messages'][0])
                    self.action(child, 'recall', dict(query=spec['prompt'], scope='both'), automatic=True)
                    pending[pool.submit(self.infer, child, cancel)] = child
                while pending:
                    self.parent.set('waiting')
                    completed, _ = wait(pending, timeout=.1, return_when=FIRST_COMPLETED)
                    for future in completed:
                        child = pending.pop(future)
                        task = child['task']
                        try:
                            reply = future.result()
                            child['messages'].append(reply)
                            child['answer'].append(reply['content'])
                            calls = reply.get('tool_calls')
                            if not calls:
                                if child['pending_copy'] or child['stopped']:
                                    raise RuntimeError('Child ended after an unresolved rejected action')
                                self.action(child, '_agent_memory', dict(text='User: '+child['prompt']+'\nAssistant: '+''.join(child['answer'])), automatic=True)
                                child['completed'] = True
                                continue
                            if child['stopped'] or child['turns'] >= 8:
                                raise PermissionError('Child action limit or post-hook stop')
                            child['turns'] += 1
                            task.set('tool')
                            call = calls[0]
                            name = call['function']['name']
                            arguments = kildall.strict_json(call['function']['arguments'])
                            if child['pending_copy'] and name != 'remember':
                                raise ValueError('Verbatim retry must correct remember')
                            issues = copy_issues(child['prompt'], name, arguments) if name == 'remember' else []
                            try:
                                if issues:
                                    with decision(task.path, self.project, name, arguments, task.id, hooks=self.hooks) as rejected:
                                        if child['retry']:
                                            raise ValueError('Verbatim copy still differs after one retry')
                                        rejected['update'](tier='Auto', status='rejected', reason='Verbatim argument requires correction')
                                    child['retry'] = child['pending_copy'] = True
                                    result = dict(error=retry_feedback(issues))
                                else:
                                    result = self.action(child, name, arguments)
                                    child['pending_copy'] = False
                            except HookFailure as error:
                                result = dict(blocked=True, action_completed=error.phase == 'after', hook_feedback=error.feedback)
                                child['stopped'] = error.phase == 'after'
                            feedback = dict(role='tool', tool_call_id=call['id'], content=json.dumps(result))
                            child['messages'].append(feedback)
                            task.message(feedback)
                            pending[pool.submit(self.infer, child, cancel)] = child
                        except Exception as error:
                            child['error'] = str(error)
                            if isinstance(error, HookFailure):
                                child.setdefault('automatic_feedback', []).append(dict(hook_feedback=error.feedback))
                            task.finish('error')
            finally:
                cancel.cancel()
                pool.shutdown(wait=True, cancel_futures=True)
                for child in children:
                    jobs = stop_jobs(self.parent.path, child['task'].id)
                    if jobs:
                        child['cancelled_jobs'] = jobs
                        child.setdefault('error', 'Unfinished child background jobs were cancelled')
                    if not child['task'].finished.is_set():
                        outcome = 'error' if child.get('error') else 'done'
                        child['task'].finish(outcome if child.get('completed') else 'cancelled')
                for slot in work[:active_shared]:
                    wait_idle(self.config, slot)
        results = []
        for child in children:
            result = dict(id=child['task'].id, text=''.join(child['answer']), error=child.get('error'), timings=child['timings'])
            if child.get('cancelled_jobs'):
                result['cancelled_jobs'] = child['cancelled_jobs']
            if child.get('automatic_feedback'):
                result['hook_feedback'] = child['automatic_feedback']
            with kildall.database(self.parent.path) as db:
                db.execute('UPDATE orbi_agents SET result=? WHERE task=?', (json.dumps(result), child['task'].id))
            results.append({key: value for key, value in result.items() if key != 'timings'})
        return dict(source='child_results', results=results)
