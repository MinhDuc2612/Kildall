"""Actual local HTTP verifies router/work admission; no model or private data."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import copy
import http.client
import json
import threading
import time
from unittest.mock import Mock, patch

import benchmark
import kildall
import routing
import subagents
import tool_runtime


def main():
    sent, active, peaks = [], {0: 0, 1: 0, 2: 0}, {0: 0, 1: 0, 2: 0}
    lock = threading.Lock()
    fail_stream, busy_poll = threading.Event(), threading.Event()
    overlaps = []
    concurrent_gate, work_overlap = None, threading.Event()
    class Handler(BaseHTTPRequestHandler):
        def reply(self, value, *, stream=False):
            data = json.dumps(value).encode()
            if stream: data = b'data: ' + data + b'\n\n'
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream' if stream else 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        def do_GET(self):
            assert self.path == '/slots'
            with lock:
                value = [dict(id=i, n_ctx=4096, is_processing=bool(active[i])) for i in active]
                if any(active.values()): busy_poll.set()
            self.reply(value)
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            if self.path == '/apply-template':
                self.reply(dict(prompt='<|turn>user\nhello<turn|>\n<|turn>model\n')); return
            if self.path == '/tokenize':
                self.reply(dict(tokens=[1])); return
            slot = body['id_slot']  # Missing admission fails this actual wire check.
            with lock:
                sent.append(dict(path=self.path, body=body))
                if active[slot]: overlaps.append(slot)
                active[slot] += 1
                peaks[slot] = max(peaks[slot], active[slot])
                if active[1] and active[2]: work_overlap.set()
            failed = False
            try:
                if concurrent_gate is not None and self.path == '/completion':
                    concurrent_gate.wait(timeout=2)
                time.sleep(.05)
                timing = dict(predicted_n=1, predicted_ms=10, predicted_per_second=100)
                if self.path == '/completion':
                    if body.get('stream') and fail_stream.is_set():
                        fail_stream.clear(); failed = True
                        self.reply(dict(content='partial'), stream=True); return
                    self.reply(dict(content='ok', tokens=[], stop=True, stop_type='eos', timings=timing),
                               stream=body.get('stream', False)); return
                assert self.path == '/v1/chat/completions'
                if 'response_format' in body:
                    content = json.dumps(dict(skill='general_assistance'))
                else:
                    content = 'general_assistance:X' if body.get('grammar') else 'ok'
                self.reply(dict(choices=[dict(message=dict(role='assistant', content=content), finish_reason='stop')], timings=timing))
            finally:
                def drain():
                    with lock: active[slot] -= 1
                if failed:
                    timer = threading.Timer(.2, drain)
                    timer.daemon = True; timer.start()
                else: drain()
        def log_message(self, *args): pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    config = kildall.settings()
    config['runtime'] = dict(config['runtime'], port=server.server_port, parallel=2)
    endpoint = kildall.url(config)
    body = dict(messages=[dict(role='user', content='hello')], tools=kildall.BASE_TOOLS,
                max_tokens=8, stream=False, temperature=0, tool_choice='auto')
    original = copy.deepcopy(body)
    try:
        with patch.object(kildall, 'settings', return_value=config):
            for action in (
                lambda: kildall.json_request(endpoint+'/v1/chat/completions', dict(messages=[])),
                lambda: tool_runtime.chat(endpoint, body),
                lambda: benchmark.chat(endpoint, [dict(role='user', content='hello')]),
            ):
                action(); assert sent[-1]['body']['id_slot'] == 1
            assert body == original
            with subagents.turn_slot(config):
                routing.classify_catalog(config, 'hello')
                assert sent[-1]['body']['id_slot'] == 0
                routing.classify(config, 'classify', 'hello', dict(skill=dict(type='string', enum=['general_assistance'])))
                assert sent[-1]['body']['id_slot'] == 0
                kildall.json_request(endpoint+'/completion', dict(prompt='hello'))
                assert sent[-1]['body']['id_slot'] == 1
            for invalid in (0, -1, 2):
                before = len(sent)
                for action in (
                    lambda: kildall.json_request(endpoint+'/completion', dict(prompt='hello', id_slot=invalid)),
                    lambda: tool_runtime.chat(endpoint, dict(body, id_slot=invalid)),
                    lambda: benchmark.chat(endpoint, [], id_slot=invalid),
                ):
                    try: action()
                    except ValueError: pass
                    else: raise AssertionError('Caller escaped its work slot')
                assert len(sent) == before
            with ThreadPoolExecutor(max_workers=2) as pool:
                replies = list(pool.map(lambda _: kildall.json_request(endpoint+'/completion', dict(prompt='hello')), range(4)))
            assert len(replies) == 4 and peaks[1] == 1
            assert sum(r['body']['id_slot'] == 0 for r in sent) == 2
            manager = subagents.Manager(config, None, None, '/fixture', kildall.BASE_TOOLS)
            children = [dict(task=Mock(), config=config, slot=1, memory='', timings=[],
                             messages=[dict(role='user', content=name)]) for name in ('first', 'queued')]
            cancel = subagents.Cancellation()
            fail_stream.set(); busy_poll.clear()
            with subagents.turn_slot(config), ThreadPoolExecutor(max_workers=1) as pool:
                first, queued = [pool.submit(manager.infer, child, cancel) for child in children]
                try: first.result(timeout=3)
                except RuntimeError as error:
                    assert 'without a completed response' in str(error), error
                else: raise AssertionError('Incomplete child stream was accepted')
                assert queued.result(timeout=3)['content'] == 'ok'
            assert busy_poll.is_set() and not overlaps, 'Queued child reused an undrained failed slot'
            busy_poll.clear()
            with lock: active[1] += 1
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    pending = pool.submit(subagents.wait_idle, config, 1, cancel=cancel)
                    assert busy_poll.wait(1), 'Idle wait never checked the busy slot'
                    cancel.cancel()
                    try: pending.result(timeout=1)
                    except (InterruptedError, OSError, http.client.HTTPException):
                        assert cancel.stopped.is_set()
                    else: raise AssertionError('Cancelled idle wait was allowed to continue')
            finally:
                with lock: active[1] -= 1
            three = copy.deepcopy(config); three['runtime']['parallel'] = 3
            assert subagents.work_slots(three) == (1, 2)
            manager = subagents.Manager(three, None, None, '/fixture', kildall.BASE_TOOLS)
            children = [dict(task=Mock(), config=three, slot=slot, memory='', timings=[],
                             messages=[dict(role='user', content=f'work {slot}')]) for slot in (1, 2)]
            with subagents.turn_slot(three), subagents.lease(three, 2):
                routing.classify_catalog(three, 'hello')
                assert sent[-1]['body']['id_slot'] == 0
                before = len(sent)
                concurrent_gate = threading.Barrier(2)
                try:
                    with ThreadPoolExecutor(max_workers=2) as pool:
                        futures = [pool.submit(manager.infer, child, subagents.Cancellation()) for child in children]
                        assert all(future.result(timeout=3)['content'] == 'ok' for future in futures)
                finally: concurrent_gate = None
            assert work_overlap.is_set() and not overlaps
            assert len(sent[before:]) == 2 and {r['body']['id_slot'] for r in sent[before:]} == {1, 2}
            one = copy.deepcopy(config); one['runtime']['parallel'] = 1
            with patch.object(kildall, 'settings', return_value=one), subagents.turn_slot(one):
                routing.classify_catalog(one, 'hello')
                assert sent[-1]['body']['id_slot'] == 0
                tool_runtime.chat(endpoint, body)
                assert sent[-1]['body']['id_slot'] == 0
            try: subagents.inference_body(endpoint+'/completion', {})
            except ValueError: pass
            else: raise AssertionError('Unowned generation accepted')
    finally:
        server.shutdown(); server.server_close(); thread.join()
    print('PASS: router/work admission, no unpinned requests, A serialized work, B concurrent work1+2 with router0 isolated, failed-child drain before queued reuse, cancellable idle wait, one-slot compatibility')


if __name__ == '__main__': main()
