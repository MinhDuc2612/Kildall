"""Prefix-only router persistence and best-effort, foreground-preemptible maintenance."""
from contextlib import contextmanager
from contextvars import ContextVar
import fcntl
import hashlib
import http.client
import json
import os
from pathlib import Path
import signal
import socket
import stat
import struct
import subprocess
import sys
import threading
import time
import uuid
import urllib.request
from urllib.parse import urlsplit

MAINTENANCE = ContextVar('router_maintenance', default=False)


def files(port):
    from kildall import ROOT
    return ROOT / '.session' / f'warmth-{port}'


def notify(endpoint, message=b'yield'):
    target = urlsplit(endpoint)
    if target.hostname != '127.0.0.1' or target.scheme != 'http':
        return
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
            sock.setblocking(False)
            sock.sendto(message, str(files(target.port)) + '.sock')
    except (OSError, ValueError):
        pass  # Optional maintenance must never make foreground inference fail.


@contextmanager
def foreground(endpoint):
    """Hold an activity lease, but never wait for a warming request or worker."""
    target = urlsplit(endpoint)
    base = files(target.port) if target.hostname == '127.0.0.1' else None
    if MAINTENANCE.get() or base is None or not base.with_suffix('.sock').exists():
        yield
        return
    with base.with_suffix('.activity').open('a') as lock:
        notify(endpoint)
        try:
            fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            # The worker's probe cannot delay the user, even if it is descheduled.
            pass
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def completed(endpoint, body, response):
    """Send only a validity bit; never send a user's prompt to the sidecar."""
    if MAINTENANCE.get() or body.get('id_slot') != 0:
        return
    from routing import catalog_prompt
    messages = body.get('messages', [])
    valid = (len(messages) == 2 and messages[0] == dict(role='system', content=catalog_prompt()[0])
             and messages[1].get('role') == 'user' and response is not None)
    notify(endpoint, b'catalog' if valid else b'dirty')


def digest(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def cache_key(config, command):
    from routing import catalog_prompt
    import skill_catalog
    policy, grammar = catalog_prompt()
    return dict(model=digest(config['lanes']['a']['model']),
                prompt=hashlib.sha256(policy.encode()).hexdigest(),
                catalog=digest(skill_catalog.__file__), grammar=hashlib.sha256(grammar.encode()).hexdigest(),
                flags=command, binary=digest(config['runtime']['server']))


def prefix(config):
    from kildall import json_request, url
    from routing import catalog_prompt
    endpoint = url(config)
    rendered = json_request(endpoint + '/apply-template', dict(
        messages=[dict(role='system', content=catalog_prompt()[0])], add_generation_prompt=False))['prompt']
    # Native string/chat requests add BOS; token arrays do not. Match native tokens exactly.
    return json_request(endpoint + '/tokenize', dict(content=rendered, add_special=True))['tokens']


def saved_tokens(path):
    """Validate b10809's text-only server_tokens envelope, not just a byte-string grep."""
    if not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Router slot must be a regular file')
    with path.open('rb') as source:
        magic, version, size = struct.unpack('<III', source.read(12))
        if magic != 1734833009 or version != 3 or not 4 <= size <= 4100:
            raise ValueError('Unexpected b10809 slot header')
        packed = struct.unpack(f'<{size}i', source.read(size * 4))
    if packed[:2] != (-1, 1) or packed[2] != size - 4 or packed[-1] != 0:
        raise ValueError('Expected a text-only b10809 token envelope')
    return list(packed[3:-1])


def valid_file(directory, key, tokens):
    from kildall import strict_json
    try:
        manifest = strict_json((directory / 'prefix.json').read_text())
        path = directory / 'prefix.bin'
        return (manifest['key'] == key and saved_tokens(path) == tokens
                and manifest['sha256'] == digest(path))
    except (OSError, ValueError, KeyError, TypeError, struct.error):
        return False


def warm(config, tokens, *, cancel=None):
    from kildall import json_request, strict_json, url
    body = dict(prompt=tokens, n_predict=0, temperature=0, top_p=1,
                samplers=['temperature'], seed=42, cache_prompt=False, stream=False)
    started = time.monotonic()
    if cancel is None:
        response = json_request(url(config) + '/completion', body, timeout=180)
    else:
        from subagents import inference_body
        # b10809 notices a closed non-stream client too late during prefill.
        # Progress writes expose disconnects after each batch and cancel the task.
        endpoint = url(config) + '/completion'
        body.update(stream=True, return_progress=True)
        request = urllib.request.Request(endpoint, json.dumps(inference_body(endpoint, body)).encode(),
                                         {'Content-Type': 'application/json'})
        response = None
        with cancel.open(request, timeout=180) as stream:
            for line in stream:
                cancel.check()
                if len(line) > 1_000_000:
                    raise ValueError('Oversized router warm progress event')
                if line.startswith(b'data:'):
                    event = strict_json(line[5:])
                    if 'error' in event:
                        raise RuntimeError('Router warm stream failed')
                    if event.get('stop') is True:
                        response = event
                        break
        if response is None:
            raise RuntimeError('Incomplete router warm stream')
    # b10809 samples one token even at n_predict=0; it is not inserted into saved KV.
    if response.get('tokens_evaluated') != len(tokens):
        raise ValueError('Incomplete router prefix warm-up')
    return dict(seconds=time.monotonic() - started, timings=response['timings'])


def initialize(config, record, command):
    from kildall import atomic_json, json_request, url
    from subagents import router_slot
    directory = config['paths']['code_dir'] / '.session' / 'router-prefix'
    started = time.monotonic()
    key = cache_key(config, command)
    tokens = prefix(config)
    status = dict(restored=False, stale_rejected=False)
    token = MAINTENANCE.set(True)
    try:
        with router_slot(config):
            if valid_file(directory, key, tokens):
                try:
                    restored = json_request(url(config) + '/slots/0?action=restore', dict(filename='prefix.bin'))
                    status['restored'] = restored['n_restored'] == len(tokens)
                except (OSError, ValueError, RuntimeError):
                    status['restore_failed'] = True
            else:
                status['stale_rejected'] = (directory / 'prefix.bin').exists()
            # b10809 disk state omits SWA checkpoints: rebuild before advertising readiness.
            json_request(url(config) + '/slots/0?action=erase', {})
            status['checkpoint_rebuild'] = warm(config, tokens)
            pending = directory / ('prefix-' + uuid.uuid4().hex + '.pending')
            if pending.exists() or pending.is_symlink():
                raise ValueError('Router save destination already exists')
            json_request(url(config) + '/slots/0?action=save', dict(filename=pending.name))
            if saved_tokens(pending) != tokens:
                raise ValueError('Refusing to persist anything beyond the router prefix')
            saved = dict(key=key, sha256=digest(pending), tokens=len(tokens), bytes=pending.stat().st_size)
            pending.replace(directory / 'prefix.bin')
            atomic_json(directory / 'prefix.json', saved)
    finally:
        MAINTENANCE.reset(token)
    status.update(startup_seconds=time.monotonic() - started, file_bytes=saved['bytes'], prefix_tokens=len(tokens))
    atomic_json(directory / 'startup.json', status)
    worker = dict(config=dict(runtime={k: config['runtime'][k] for k in ('port', 'parallel', 'context_size')},
                              paths=dict(code_dir=str(config['paths']['code_dir']))),
                  server=record, tokens=tokens, valid=True)
    atomic_json(directory / 'worker.json', worker)
    start_monitor(config, record, fresh=True)


def owns_worker(record):
    from kildall import process_start
    if not record or process_start(record['pid']) != record['started']:
        return False
    result = subprocess.run(['ps', '-p', str(record['pid']), '-o', 'command='], capture_output=True, text=True)
    return result.returncode == 0 and str(Path(__file__).resolve()) in result.stdout


def stop_monitor(config):
    from kildall import strict_json
    path = files(config['runtime']['port']).with_suffix('.json')
    if not path.exists():
        return
    record = strict_json(path.read_text())
    if owns_worker(record):
        os.kill(record['pid'], signal.SIGTERM)
        deadline = time.monotonic() + 5
        while owns_worker(record) and time.monotonic() < deadline:
            time.sleep(.05)
        if owns_worker(record):
            raise TimeoutError('Router maintenance did not stop')
    path.unlink(missing_ok=True)


def start_monitor(config, server, *, fresh=False):
    from kildall import atomic_json, process_start, strict_json
    base = files(config['runtime']['port'])
    state = base.with_suffix('.json')
    if state.exists():
        record = strict_json(state.read_text())
        if owns_worker(record) and record['server'] == server:
            return
        stop_monitor(config)
    directory = config['paths']['code_dir'] / '.session' / 'router-prefix'
    worker = directory / 'worker.json'
    if not worker.exists():
        raise RuntimeError('Router startup state missing; stop and restart the runtime')
    data = strict_json(worker.read_text())
    if data['server'] != server:
        raise RuntimeError('Router maintenance belongs to an earlier server')
    data['valid'] = fresh
    atomic_json(worker, data)
    base.with_suffix('.sock').unlink(missing_ok=True)
    with (directory / 'worker.log').open('ab') as log:
        process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(worker)],
            stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
    atomic_json(state, dict(pid=process.pid, started=process_start(process.pid), server=server))
    deadline = time.monotonic() + 5
    while not base.with_suffix('.sock').exists():
        if process.poll() is not None or time.monotonic() > deadline:
            raise RuntimeError('Router maintenance failed to start')
        time.sleep(.02)


def monitor(path):
    from kildall import atomic_json, json_request, owns_server, strict_json, url
    from subagents import Cancellation, lease, bind_slot
    data = strict_json(path.read_text())
    config, tokens = data['config'], data['tokens']
    config['paths']['code_dir'] = Path(config['paths']['code_dir'])
    endpoint = url(config)
    base = files(config['runtime']['port'])
    stopped = threading.Event()
    state_lock = threading.Lock()
    current = [None]
    valid = [data['valid']]  # A recovered monitor cannot trust its earlier validity bit.
    last = [time.monotonic()]
    shutdown = [False]

    def cancel(*_):
        stopped.set()
        with state_lock:
            if current[0] is not None:
                current[0].cancel()

    def listen(sock):
        while not shutdown[0] and not stopped.is_set():
            try:
                message = sock.recv(32)
            except socket.timeout:
                continue
            with state_lock:
                last[0] = time.monotonic()
                if current[0] is not None:
                    current[0].cancel()
                if message in (b'dirty', b'catalog'):
                    valid[0] = message == b'catalog'
        cancel()

    # A signal must not reacquire a lock held by the interrupted main thread.
    signal.signal(signal.SIGTERM, lambda *_: shutdown.__setitem__(0, True))
    signal.signal(signal.SIGINT, lambda *_: shutdown.__setitem__(0, True))
    with base.with_suffix('.worker-lock').open('a') as singleton, socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
        fcntl.flock(singleton, fcntl.LOCK_EX | fcntl.LOCK_NB)
        address = base.with_suffix('.sock')
        address.unlink(missing_ok=True)
        sock.bind(str(address))
        os.chmod(address, 0o600)
        sock.settimeout(.2)
        listener = threading.Thread(target=listen, args=(sock,), daemon=True)
        listener.start()
        try:
            while not stopped.wait(.25) and owns_server(data['server']):
                cancellation = Cancellation()
                with state_lock:
                    if time.monotonic() - last[0] < 1:
                        continue
                    current[0] = cancellation
                maintenance = MAINTENANCE.set(True)
                try:
                    # Probe only: never hold this exclusive lock across HTTP or compute.
                    with base.with_suffix('.activity').open('a') as lock:
                        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    slots = json_request(endpoint + '/slots', timeout=1, cancel=cancellation)
                    if any(row['is_processing'] for row in slots):
                        continue
                    router = next(row for row in slots if row['id'] == 0)
                    if valid[0] and router.get('n_prompt_tokens', 0) >= len(tokens):
                        continue
                    with lease(config, 0, blocking=False, cancel=cancellation), bind_slot(endpoint, 0, config['runtime']['parallel']):
                        cancellation.check()
                        with state_lock:
                            valid[0] = False
                        result = warm(config, tokens, cancel=cancellation)
                        with state_lock:
                            cancellation.check()
                            valid[0] = True
                        atomic_json(path.parent / 'idle.json', dict(status='warmed', **result))
                except BlockingIOError:
                    pass  # Foreground ownership is normal, not a failed maintenance run.
                except (OSError, ValueError, RuntimeError, StopIteration, http.client.HTTPException) as error:
                    # Keep only error type, never an HTTP body or user text.
                    atomic_json(path.parent / 'idle.json', dict(status='cancelled' if cancellation.stopped.is_set() else 'failed',
                                                              error=type(error).__name__))
                    last[0] = time.monotonic()
                finally:
                    MAINTENANCE.reset(maintenance)
                    with state_lock:
                        current[0] = None
        finally:
            cancel()
            listener.join(timeout=1)
            address.unlink(missing_ok=True)


if __name__ == '__main__':
    sys.modules['router_warmth'] = sys.modules[__name__]
    monitor(Path(sys.argv[1]))
