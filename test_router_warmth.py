"""Router prefix integrity, foreground priority and monitor lifecycle; no model."""
from contextlib import nullcontext
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import copy
import fcntl
import json
from pathlib import Path
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

import kildall
import router_warmth as warmth
import routing
import skill_catalog
import subagents


TOKENS = [2, 105, 17, 106, 107]
CANARY = 'PRIVATE_USER_CANARY_NEVER_PERSIST'


def until(predicate, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if value := predicate():
            return value
        time.sleep(.02)
    raise AssertionError('Timed out waiting for router maintenance')


def slot_file(path, tokens=TOKENS):
    packed = [-1, 1, len(tokens), *tokens, 0]
    path.write_bytes(struct.pack('<III', 1734833009, 3, len(packed))
                     + struct.pack(f'<{len(packed)}i', *packed) + b'FAKE_KV')


def persist(directory, key):
    slot_file(directory / 'prefix.bin')
    kildall.atomic_json(directory / 'prefix.json', dict(
        key=key, sha256=warmth.digest(directory / 'prefix.bin')))


def integrity(root):
    directory = root / 'integrity'
    directory.mkdir()
    model, binary, catalog = [directory / name for name in ('model', 'server', 'catalog')]
    for path in (model, binary, catalog):
        path.write_bytes(path.name.encode())
    config = dict(lanes=dict(a=dict(model=model)), runtime=dict(server=binary))
    command = ['llama-server', '-np', '3', '-c', '12288']
    with patch.object(skill_catalog, '__file__', str(catalog)), \
         patch.object(routing, 'catalog_prompt', return_value=('policy', 'grammar')):
        key = warmth.cache_key(config, command)
        for field, path in [('model', model), ('binary', binary), ('catalog', catalog)]:
            original = path.read_bytes()
            path.write_bytes(b'x' * len(original))
            changed = warmth.cache_key(config, command)
            assert changed[field] != key[field]
            assert {name for name in key if key[name] != changed[name]} == {field}
            path.write_bytes(original)
        with patch.object(routing, 'catalog_prompt', return_value=('changed', 'grammar')):
            assert warmth.cache_key(config, command)['prompt'] != key['prompt']
        with patch.object(routing, 'catalog_prompt', return_value=('policy', 'changed')):
            assert warmth.cache_key(config, command)['grammar'] != key['grammar']
        assert warmth.cache_key(config, [*command, '--changed'])['flags'] != key['flags']
    persist(directory, key)
    assert warmth.saved_tokens(directory / 'prefix.bin') == TOKENS
    assert warmth.valid_file(directory, key, TOKENS)
    for field in key:
        changed = dict(key, **{field: ['changed'] if field == 'flags' else 'changed'})
        assert not warmth.valid_file(directory, changed, TOKENS), field
    path = directory / 'prefix.bin'
    original = path.read_bytes()
    path.write_bytes(original[:-1] + b'X')
    assert not warmth.valid_file(directory, key, TOKENS), 'KV corruption accepted'
    slot_file(path, [*TOKENS, 999])
    manifest = dict(key=key, sha256=warmth.digest(path))
    kildall.atomic_json(directory / 'prefix.json', manifest)
    assert not warmth.valid_file(directory, key, TOKENS), 'Non-prefix tokens accepted'
    for damaged in (b'', original[:14], struct.pack('<III', 0, 3, 9),
                    struct.pack('<III', 1734833009, 3, 999999)):
        path.write_bytes(damaged)
        assert not warmth.valid_file(directory, key, TOKENS), 'Invalid envelope accepted'
    outside = root / 'outside-slot'
    slot_file(outside)
    path.unlink()
    path.symlink_to(outside)
    kildall.atomic_json(directory / 'prefix.json', dict(key=key, sha256=warmth.digest(outside)))
    assert not warmth.valid_file(directory, key, TOKENS), 'Outward slot symlink accepted'
    assert outside.read_bytes() == original
    print('PASS: full model/prompt/catalog/grammar/flags/binary key; exact token envelope; stale, corrupt and outward-link rejection')


def initialization(root):
    config = dict(runtime=dict(port=19237, parallel=3, context_size=4096), paths=dict(code_dir=root))
    directory = root / '.session' / 'router-prefix'
    directory.mkdir(parents=True, exist_ok=True)
    key = dict(model='model', prompt='prompt', catalog='catalog', flags=['fixed'], grammar='grammar', binary='binary')
    record = dict(pid=99999999, started='fixture', model='fixture')
    requests, fail_restore, invalid_save = [], False, False

    def request(endpoint, body=None, **kwargs):
        requests.append((endpoint, copy.deepcopy(body)))
        assert CANARY not in json.dumps(body)
        if endpoint.endswith('/apply-template'):
            assert body == dict(messages=[dict(role='system', content='policy')], add_generation_prompt=False)
            return dict(prompt='prefix')
        if endpoint.endswith('/tokenize'):
            assert body == dict(content='prefix', add_special=True)
            return dict(tokens=TOKENS)
        if endpoint.endswith('action=restore'):
            if fail_restore:
                raise RuntimeError('fixture restore failure')
            return dict(n_restored=len(TOKENS))
        if endpoint.endswith('action=erase'):
            assert body == {}
            return {}
        if endpoint.endswith('/completion'):
            assert body['prompt'] == TOKENS and body['n_predict'] == 0
            assert body['cache_prompt'] is False and 'messages' not in body
            return dict(tokens_evaluated=len(TOKENS), timings=dict(prompt_n=len(TOKENS)))
        if endpoint.endswith('action=save'):
            slot_file(directory / body['filename'], [*TOKENS, 999] if invalid_save else TOKENS)
            return dict(n_saved=len(TOKENS))
        raise AssertionError(endpoint)

    with patch.object(warmth, 'cache_key', return_value=key), \
         patch.object(routing, 'catalog_prompt', return_value=('policy', 'grammar')), \
         patch.object(kildall, 'json_request', side_effect=request), \
         patch.object(subagents, 'router_slot', side_effect=lambda _: nullcontext()), \
         patch.object(warmth, 'start_monitor') as start:
        for field in key:
            stale = dict(key, **{field: ['old'] if field == 'flags' else 'old'})
            persist(directory, stale)
            requests.clear()
            warmth.initialize(config, record, ['fixed'])
            assert not any('action=restore' in endpoint for endpoint, _ in requests), field
            assert warmth.valid_file(directory, key, TOKENS)
            assert kildall.strict_json((directory / 'startup.json').read_text())['stale_rejected']
            assert warmth.MAINTENANCE.get() is False
        requests.clear()
        fail_restore = True
        warmth.initialize(config, record, ['fixed'])
        status = kildall.strict_json((directory / 'startup.json').read_text())
        assert status['restore_failed'] and not status['restored']
        assert [endpoint.rsplit('/', 1)[-1] for endpoint, _ in requests[-4:]] == [
            '0?action=restore', '0?action=erase', 'completion', '0?action=save']
        assert warmth.saved_tokens(directory / 'prefix.bin') == TOKENS
        assert CANARY.encode() not in (directory / 'prefix.bin').read_bytes()
        assert start.call_count == len(key) + 1
        fail_restore = False
        warmth.initialize(config, record, ['fixed'])
        assert kildall.strict_json((directory / 'startup.json').read_text())['restored']
        original = (directory / 'prefix.bin').read_bytes()
        invalid_save = True
        before = start.call_count
        try:
            warmth.initialize(config, record, ['fixed'])
        except ValueError as error:
            assert 'router prefix' in str(error)
        else:
            raise AssertionError('Persistence accepted extra non-prefix tokens')
        assert (directory / 'prefix.bin').read_bytes() == original
        assert start.call_count == before and warmth.MAINTENANCE.get() is False
    print('PASS: every stale key bypasses restore; restore success/failure rebuilds; non-prefix save rejected before replacement or worker start')


def foreground(root):
    config = dict(runtime=dict(port=19238, parallel=3), paths=dict(code_dir=root))
    endpoint = kildall.url(config)
    base = warmth.files(config['runtime']['port'])
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as listener:
        listener.bind(str(base.with_suffix('.sock')))
        listener.settimeout(.3)

        def held():
            with base.with_suffix('.activity').open('a') as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    return
                raise AssertionError('Foreground activity lease was not held')

        with subagents.bind_slot(endpoint, 2, 3), subagents.request_slot(endpoint + '/completion'):
            assert listener.recv(32) == b'yield'
            held()
        with patch.object(subagents, 'wait_idle', side_effect=lambda *args, **kwargs: held()):
            with subagents.lease(config, 1):
                assert listener.recv(32) == b'yield'
                held()
        with base.with_suffix('.activity').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            started = time.monotonic()
            with warmth.foreground(endpoint):
                assert listener.recv(32) == b'yield'
            assert time.monotonic() - started < .1, 'Worker activity probe blocked foreground'
        warmth.completed(endpoint, dict(id_slot=0, messages=[dict(role='system', content=routing.catalog_prompt()[0]),
                                                           dict(role='user', content=CANARY)]), {})
        assert listener.recv(32) == b'catalog'
        warmth.completed(endpoint, dict(id_slot=0, prompt=CANARY), {})
        assert listener.recv(32) == b'dirty'
        token = warmth.MAINTENANCE.set(True)
        try:
            with warmth.foreground(endpoint):
                with base.with_suffix('.activity').open('a') as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            warmth.completed(endpoint, dict(id_slot=0, prompt=CANARY), {})
        finally:
            warmth.MAINTENANCE.reset(token)
        try:
            listener.recv(32)
        except socket.timeout:
            pass
        else:
            raise AssertionError('Maintenance announced itself as foreground')
    base.with_suffix('.sock').unlink()
    print('PASS: bound-slot and lease callers yield immediately and hold activity leases; completion feedback contains only validity bits')


def lifecycle(root):
    warm_started, release, server_alive = threading.Event(), threading.Event(), root / 'server-alive'
    server_alive.touch()
    state = dict(warms=0, tokens=0)

    class Handler(BaseHTTPRequestHandler):
        def reply(self, data):
            raw = json.dumps(data).encode()
            self.send_response(200)
            self.send_header('Content-Length', str(len(raw)))
            self.end_headers()
            try:
                self.wfile.write(raw)
            except (BrokenPipeError, ConnectionResetError):
                pass

        def do_GET(self):
            assert self.path == '/slots'
            self.reply([dict(id=slot, n_ctx=4096, is_processing=False,
                             n_prompt_tokens=state['tokens'] if slot == 0 else 0) for slot in range(3)])

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            assert self.path == '/completion' and body['id_slot'] == 0
            assert body['prompt'] == TOKENS and CANARY not in json.dumps(body)
            assert body['stream'] is True and body['return_progress'] is True
            state['warms'] += 1
            warm_started.set()
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.end_headers()
            self.wfile.write(b'data: {"stop":false}\n\n')
            self.wfile.flush()
            release.wait(8)
            state['tokens'] = len(TOKENS)
            try:
                self.wfile.write(('data: '+json.dumps(dict(stop=True, tokens_evaluated=len(TOKENS),
                                      timings=dict(prompt_n=len(TOKENS))))+'\n\n').encode())
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    config = dict(runtime=dict(port=server.server_port, parallel=3, context_size=4096), paths=dict(code_dir=root))
    record = dict(pid=99999999, started='fixture', model='fixture')
    directory = root / '.session' / 'router-prefix'
    worker = directory / 'worker.json'
    base = warmth.files(server.server_port)
    children, real_popen = [], subprocess.Popen
    kildall.atomic_json(worker, dict(config=dict(runtime=config['runtime'], paths=dict(code_dir=str(root))),
                                    server=record, tokens=TOKENS, valid=False))

    def spawn(command, **kwargs):
        if command[1] != str(Path(warmth.__file__).resolve()):
            return real_popen(command, **kwargs)
        child = real_popen([command[0], str(Path(__file__).resolve()), '--monitor-fixture', command[2], command[1]], **kwargs)
        children.append(child)
        return child

    try:
        with patch.object(warmth.subprocess, 'Popen', side_effect=spawn):
            warmth.start_monitor(config, record)
            saved = kildall.strict_json(base.with_suffix('.json').read_text())
            assert warmth.owns_worker(saved)
            warmth.start_monitor(config, record)
            assert len(children) == 1, 'Duplicate worker started'
            assert warm_started.wait(4), 'Idle missing prefix was not rebuilt'
            idle = directory / 'idle.json'
            start = time.monotonic()
            with warmth.foreground(kildall.url(config)):
                until(lambda: idle.exists() and kildall.strict_json(idle.read_text()).get('status') == 'cancelled', 1)
                assert time.monotonic() - start < 1, 'Foreground waited for the blocked HTTP completion'
                time.sleep(1.2)
                assert state['warms'] == 1, 'Maintenance restarted while foreground held its lease'
            release.set()
            warmth.notify(kildall.url(config), b'dirty')
            until(lambda: idle.exists() and kildall.strict_json(idle.read_text()).get('status') == 'warmed')
            assert state['warms'] >= 2
            warmth.stop_monitor(config)
            assert children[-1].wait(timeout=3) == 0
            assert not base.with_suffix('.sock').exists() and not base.with_suffix('.json').exists()
            warmth.start_monitor(config, record)
            server_alive.unlink()
            assert children[-1].wait(timeout=4) == 0, 'Monitor survived its server'
            warmth.stop_monitor(config)
    finally:
        release.set()
        for child in children:
            if child.poll() is None:
                child.terminate()
            child.wait(timeout=5)
        server.shutdown()
        server.server_close()
        thread.join()
    print('PASS: real monitor process singleton, cancellable HTTP warm-up, foreground priority, idle recovery, clean stop and server-death exit')


def main():
    with tempfile.TemporaryDirectory(prefix='kw-', dir='/tmp') as directory:
        root = Path(directory)
        (root / '.session').mkdir()
        with patch.object(kildall, 'ROOT', root):
            integrity(root)
            initialization(root)
            foreground(root)
            lifecycle(root)
    print('PASS: router warmth controls (no model loaded)')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor-fixture':
        worker = Path(sys.argv[2])
        root = worker.parents[2]
        with patch.object(kildall, 'ROOT', root), \
             patch.object(kildall, 'owns_server', side_effect=lambda _: (root / 'server-alive').exists()):
            warmth.monitor(worker)
    else:
        main()
