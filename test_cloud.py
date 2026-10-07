"""Cloud gates using localhost HTTP only; no credentials, models or paid calls."""
from contextlib import ExitStack, redirect_stderr, redirect_stdout
import copy
import datetime
import email.utils
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import queue
import tempfile
import threading
import time
import urllib.request
from unittest.mock import Mock, patch

import cloud
import cloud_keys
import kildall
import permissions


FAKE_KEY = 'test-only-provider-credential-42891'
NOW = 1_800_000_000


def response(message=None, **extra):
    return dict(choices=[dict(message=message or dict(role='assistant', content='answer'),
                             finish_reason='tool_calls' if message and message.get('tool_calls') else 'stop')],
                **extra)


def tool(name='read_file', arguments=None):
    return dict(role='assistant', content='', tool_calls=[dict(id='test-call', type='function',
        function=dict(name=name, arguments=json.dumps(arguments or {'path': 'a.txt'})))])


def config(work, names=('llm7',)):
    items = {}
    for name in names:
        base, key, models = cloud.PROVIDERS[name]
        items[name] = dict(base_url=base, key_name=key, allowed_models=[sorted(models)[0]],
                           context_tokens=100_000, limits_status='unverified', trains_on_data='unknown',
                           daily_requests=0, daily_tokens=0)
    return dict(paths=dict(db_path=work / 'test.db'), cloud=dict(enabled=True, providers=items))


class HTTPFixture:
    """Real HTTP responses; adapter retains validation of production endpoints."""
    def __init__(self):
        self.pending, self.captured = queue.Queue(), []
        self.release = threading.Event()
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                fixture.captured.append(dict(path=self.path, headers=dict(self.headers),
                    body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
                try:
                    status, body, headers, delayed = fixture.pending.get_nowait()
                except queue.Empty:
                    status, body, headers, delayed = 599, {}, {}, False
                if delayed:
                    fixture.release.wait(.3)
                self.send_response(status)
                for name, value in headers.items():
                    self.send_header(name, value)
                self.end_headers()
                try:
                    self.wfile.write(json.dumps(body).encode())
                except (BrokenPipeError, ConnectionResetError):
                    pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
        self.thread.start()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), cloud.NoRedirect())

    def add(self, status=200, body=None, headers=None, delay=False):
        self.pending.put((status, response() if body is None else body, headers or {}, delay))

    def open(self, request, timeout):
        destinations = {value[0] + '/chat/completions': name for name, value in cloud.PROVIDERS.items()}
        assert request.full_url in destinations, 'Unexpected external endpoint'
        local = urllib.request.Request(f'http://127.0.0.1:{self.server.server_port}/' + destinations[request.full_url],
                                       request.data, dict(request.header_items()))
        return self.opener.open(local, timeout=.05)

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(1)


def client(conf, http):
    result = cloud.Client(conf)
    result.opener = http
    return result


def rows(conf, table='cloud_requests'):
    assert table in ('cloud_requests', 'cloud_state', 'orbi_permissions', 'orbi_messages', 'orbi_routes')
    with kildall.database(conf['paths']['db_path']) as db:
        return [dict(row) for row in db.execute('SELECT * FROM ' + table)]


def rejected(fn, kind=ValueError):
    try:
        fn()
    except kind as error:
        assert FAKE_KEY not in str(error)
        return error
    raise AssertionError('Expected rejection')


def test_http_and_redaction(work, http):
    conf = config(work)
    c = client(conf, http)
    http.add(body=response(dict(role='assistant', content='echo ' + FAKE_KEY), usage={'total_tokens': 7}))
    prompt = 'Unlabelled ' + FAKE_KEY + ' GEMINI_API_KEY=AIza' + 'a' * 30 + ' and gsk_' + 'b' * 30
    result = c.reply([dict(role='user', content=prompt)], [], 'parent-task')
    captured = json.dumps(http.captured[0]['body'])
    assert FAKE_KEY not in captured and 'AIza' not in captured and 'gsk_' not in captured
    assert '[REDACTED]' in captured and FAKE_KEY not in result['content']
    assert http.captured[0]['headers']['Authorization'] == 'Bearer ' + FAKE_KEY
    assert http.captured[0]['body']['model'] in cloud.PROVIDERS['llm7'][2]
    assert rows(conf)[0]['tokens'] == 7 and rows(conf)[0]['task'] == 'parent-task'
    assert FAKE_KEY not in conf['paths']['db_path'].read_bytes().decode('latin1')
    with patch.object(cloud_keys, 'get_key', return_value=None):
        conf = config(work, ('llm7', 'ovh'))
        http.add()
        assert client(conf, http).reply([dict(role='user', content='hello')], [])['content'] == 'answer'
        assert http.captured[-1]['path'] == '/ovh' and 'Authorization' not in http.captured[-1]['headers']
    conf = config(work)
    conf['cloud']['providers']['llm7']['keyless'] = True
    with patch.object(cloud_keys, 'get_key', return_value=None):
        http.add(body=response(dict(role='assistant', content='READY', tool_calls=None)))
        assert client(conf, http).reply([], [])['content'] == 'READY'
        assert http.captured[-1]['path'] == '/llm7' and 'Authorization' not in http.captured[-1]['headers']


def test_cooldown(work, http):
    conf = config(work)
    c = client(conf, http)
    for status, header, expected in [(429, '90', 90), (429, email.utils.formatdate(NOW + 120, usegmt=True), 120),
                                      (503, None, 60)]:
        with kildall.database(conf['paths']['db_path']) as db:
            db.execute('DELETE FROM cloud_state')
        http.add(status, {'error': {'message': 'busy ' + FAKE_KEY}}, {'Retry-After': header} if header else {})
        with patch.object(cloud.time, 'time', return_value=NOW):
            assert c.reply([], []) is None
            state = rows(conf, 'cloud_state')[0]
            assert state['cooldown'] == NOW + expected
            count = len(http.captured)
            assert client(conf, http).reply([], []) is None and len(http.captured) == count
        http.add()
        with patch.object(cloud.time, 'time', return_value=NOW + expected + 1):
            assert c.reply([], [])['content'] == 'answer'
    assert FAKE_KEY not in json.dumps(rows(conf))


def test_timeout_rotation(work, http):
    conf = config(work, ('llm7', 'ovh'))
    c = client(conf, http)
    http.add(delay=True)
    http.add()
    assert c.reply([], [])['content'] == 'answer'
    assert [r['path'] for r in http.captured] == ['/llm7', '/ovh']
    assert [r['status'] for r in rows(conf)] == ['transport_cooldown', 'answered']
    assert rows(conf)[0]['tokens'] > 512  # Uncertain usage remains conservatively reserved.


def test_invalid_credentials(work, http):
    conf = config(work)
    for status in (401, 403):
        with kildall.database(conf['paths']['db_path']) as db:
            db.execute('DROP TABLE IF EXISTS cloud_state')
        c = client(conf, http)
        http.add(status, {'error': 'invalid credential ' + FAKE_KEY})
        assert c.reply([], []) is None
        state = rows(conf, 'cloud_state')[0]
        assert state['invalid_hash'] == hashlib.sha256(FAKE_KEY.encode()).hexdigest()
        count = len(http.captured)
        assert client(conf, http).reply([], []) is None and len(http.captured) == count
        with patch.object(cloud_keys, 'get_key', return_value='replacement-test-key'):
            http.add()
            assert c.reply([], [])['content'] == 'answer'
        assert rows(conf, 'cloud_state')[0]['invalid_hash'] is None


def test_billing(work, http):
    conf = config(work)
    c = client(conf, http)
    for status, body in [(402, {'error': 'payment required'}),
                          (400, 'Payment required'),
                          (200, {'error': {'message': 'insufficient credits'}}),
                          (200, response(usage={'total_tokens': 2, 'cost': .01}))]:
        http.add(status, body)
        assert c.reply([], []) is None and rows(conf, 'cloud_state')[0]['disabled'] == 1
        count = len(http.captured)
        with patch.object(cloud_keys, 'get_key', return_value='replacement-test-key'):
            assert client(conf, http).reply([], []) is None and len(http.captured) == count
        c.enable('llm7')
        http.add()
        assert c.reply([], [])['content'] == 'answer'
    assert all(r['body']['model'] == conf['cloud']['providers']['llm7']['allowed_models'][0]
               for r in http.captured)
    rejected(lambda: c.enable('gemini'))


def test_exhausted(work, http):
    conf = config(work, ('llm7', 'ovh'))
    http.add(429)
    http.add(503)
    c = client(conf, http)
    assert c.reply([], []) is None and [r['path'] for r in http.captured] == ['/llm7', '/ovh']
    assert client(conf, http).reply([], []) is None and len(http.captured) == 2


def test_quotas(work, http):
    conf = config(work)
    item = conf['cloud']['providers']['llm7']
    c = client(conf, http)
    item['daily_requests'] = 10
    with patch.object(cloud.time, 'time', return_value=NOW):
        assert all(c.reserve('llm7', item, 'fingerprint', 1, None) for _ in range(9))
        assert client(conf, http).reserve('llm7', item, 'fingerprint', 1, None) is None
    midnight = datetime.datetime.fromtimestamp(NOW, datetime.timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp() + 86400
    with patch.object(cloud.time, 'time', return_value=midnight + 1):
        rolling = dict(item, quota_window='rolling_24h')
        assert c.reserve('llm7', rolling, 'fingerprint', 1, None) is None
        assert c.reserve('llm7', item, 'fingerprint', 1, None)
    with kildall.database(conf['paths']['db_path']) as db:
        db.execute('DELETE FROM cloud_requests')
    item.update(daily_requests=0, daily_tokens=100)
    with patch.object(cloud.time, 'time', return_value=NOW):
        assert c.reserve('llm7', item, 'fingerprint', 90, None)
        assert c.reserve('llm7', item, 'fingerprint', 1, None) is None
    with kildall.database(conf['paths']['db_path']) as db:
        db.execute('DELETE FROM cloud_requests')
    item.update(daily_tokens=0, requests_per_minute=2)
    with patch.object(cloud.time, 'time', return_value=NOW):
        assert c.reserve('llm7', item, 'fingerprint', 1, None)
        assert c.reserve('llm7', item, 'fingerprint', 1, None)
        assert c.reserve('llm7', item, 'fingerprint', 1, None) is None
    with patch.object(cloud.time, 'time', return_value=NOW + 61):
        assert c.reserve('llm7', item, 'fingerprint', 1, None)
    assert not http.captured


def test_allowlist(work, http):
    valid = config(work)
    for field, value in [('base_url', 'https://untrusted.invalid'), ('key_name', 'GROQ_API_KEY'),
                          ('allowed_models', ['paid-model']), ('allowed_models', ['codestral-latest:free']),
                          ('daily_requests', -1), ('daily_tokens', True)]:
        bad = copy.deepcopy(valid)
        bad['cloud']['providers']['llm7'][field] = value
        rejected(lambda: cloud.Client(bad))
    for name in ('gemini', 'google', 'groq'):
        bad = copy.deepcopy(valid)
        bad['cloud']['providers'][name] = bad['cloud']['providers'].pop('llm7')
        rejected(lambda: cloud.Client(bad))
    conf = config(work)
    conf['cloud']['enabled'] = False
    assert client(conf, http).reply([], []) is None and not http.captured


def test_malformed(work, http):
    for text in ('{"choices":[],"choices":[]}', '{"nested":{"a":1,"a":2}}', '{"a":NaN}'):
        rejected(lambda: cloud.decode(text))
    valid = response(tool())
    variants = []
    for arguments in ('{}', '{"path":2}', '{"path":"a","extra":true}',
                       '{"path":"a","path":"b"}', '{"path":NaN}', 'not JSON'):
        bad = copy.deepcopy(valid)
        bad['choices'][0]['message']['tool_calls'][0]['function']['arguments'] = arguments
        variants.append(bad)
    for name in ('sudo', 'git_commit', 'spawn_agent'):
        variants.append(response(tool(name)))
    for value in ([], 'string', None):
        variants.append(dict(choices=[dict(message=value, finish_reason='stop')]))
    bad = copy.deepcopy(valid)
    bad['choices'][0]['message']['tool_calls'] *= 2
    variants += [bad, {'choices': []}, {'choices': [None]}, {'choices': [{'message': {'role': 'system'}}]}]
    for bad in variants:
        http.add(body=bad)
        c = client(config(work), http)
        with patch.object(permissions, 'execute') as execute:
            rejected(lambda: c.reply([], kildall.BASE_TOOLS))
            execute.assert_not_called()
    assert len(http.captured) == len(variants)  # One rejected request; no repair request.
    assert all(r['status'] == 'malformed_rejected' for r in rows(config(work)))
    # Scrubbing a credential-bearing tool argument must reject it, never mutate it.
    http.add(body=response(tool(arguments={'path': FAKE_KEY})))
    rejected(lambda: client(config(work), http).reply([], kildall.BASE_TOOLS))


def run_turn(conf, work, *, lane='A', cloud_replies=None, prompt='Read the fixture', overflow=False):
    kildall.initialize(conf['paths']['db_path'])
    session = 'session-' + str(time.monotonic_ns())
    with kildall.database(conf['paths']['db_path']) as db:
        db.execute('INSERT INTO orbi_sessions VALUES(?,?,?)', (session, str(work), time.time()))
    memory = Mock()
    memory.retrieve.return_value = dict(text='', items=[], truncated=False)
    memory.add.return_value = 1
    decision = dict(skill='general', lane=lane, model='test-model')
    cloud_reply = Mock(side_effect=cloud_replies or [dict(role='assistant', content='cloud answer')])
    output, errors = io.StringIO(), io.StringIO()
    def fit(config, system, memory_text, previous, current, **kwargs):
        result = [dict(role='system', content=system), *current]
        if overflow:
            raise kildall.ContextOverflow(result)
        return result
    with ExitStack() as stack:
        stack.enter_context(patch.object(kildall, 'ensure_runtime'))
        stack.enter_context(patch.object(kildall, 'fit_messages', side_effect=fit))
        local = stack.enter_context(patch.object(kildall, 'stream_reply', return_value=dict(role='assistant', content='local answer')))
        stack.enter_context(patch('routing.decide', return_value=decision))
        stack.enter_context(patch.object(cloud.Client, 'reply', cloud_reply))
        stack.enter_context(redirect_stdout(output))
        stack.enter_context(redirect_stderr(errors))
        try:
            status = kildall._run_turn(conf, memory, session, str(work), prompt, route_mode='auto')
        except (ValueError, PermissionError, RuntimeError) as error:
            status = error
    return status, cloud_reply, local, memory, output.getvalue(), errors.getvalue()


def test_turn_policy(work, http):
    conf = config(work)
    status, remote, local, *_ = run_turn(conf, work)
    assert status == 0 and local.call_count == 1 and remote.call_count == 0
    for lane in ('B', 'C'):
        status, remote, local, *_ = run_turn(conf, work, lane=lane)
        assert status == 0 and remote.call_count == 1 and local.call_count == 0
        assert remote.call_args.args[1] is kildall.BASE_TOOLS
    status, remote, local, *_ = run_turn(conf, work, overflow=True)
    assert status == 0 and remote.call_count == 1 and local.call_count == 0
    status, remote, local, memory, output, errors = run_turn(conf, work, lane='C', cloud_replies=[None])
    assert status == 0 and local.call_count == 1 and cloud.EXHAUSTED in errors
    assert any(cloud.EXHAUSTED in r['payload'] for r in rows(conf, 'orbi_messages'))
    status, remote, local, memory, *_ = run_turn(conf, work, overflow=True, cloud_replies=[None])
    assert isinstance(status, kildall.ContextOverflow) and local.call_count == 0
    memory.add.assert_not_called()  # Never silently truncate an oversized request.


def test_turn_permissions(work, http):
    conf = config(work)
    marker = work / 'must-survive.txt'
    marker.write_text('original')
    calls = [tool('run_command', {'command': 'rm -rf ' + str(marker)}),
             tool('run_command', {'command': 'sudo true'}),
             tool('run_command', {'command': 'screencapture image.png'})]
    for call in calls:
        validated = cloud.validate_message(response(call), kildall.BASE_TOOLS)
        with patch.object(kildall, 'SYSTEM_RULES', ''), patch.object(permissions, 'terminal_confirm') as confirm:
            status, remote, local, *_ = run_turn(conf, work, lane='C', cloud_replies=[validated])
            assert isinstance(status, PermissionError) and remote.call_count == 1 and local.call_count == 0
            confirm.assert_not_called()
        assert marker.read_text() == 'original'
    assert len(rows(conf, 'orbi_permissions')) == len(calls)
    assert all(r['tier'] == 'Never' and r['status'] == 'refused' for r in rows(conf, 'orbi_permissions'))
    wrong = tool('remember', {'text': 'Changed wording', 'scope': 'project', 'tier': 'L1'})
    with patch.object(kildall, 'copy_issues', return_value=['verbatim mismatch']), \
         patch.object(permissions, 'execute') as execute:
        status, remote, local, memory, *_ = run_turn(conf, work, lane='C', cloud_replies=[wrong])
        assert isinstance(status, ValueError) and remote.call_count == 1 and local.call_count == 0
        execute.assert_not_called()
        memory.add.assert_not_called()


def main():
    checks = [test_http_and_redaction, test_cooldown, test_timeout_rotation, test_invalid_credentials,
              test_billing, test_exhausted, test_quotas, test_allowlist, test_malformed,
              test_turn_policy, test_turn_permissions]
    failures = []
    # A mistake in the test seam must never read the actual login Keychain.
    with patch.object(cloud_keys, '_security', side_effect=AssertionError('Keychain forbidden in test')), \
         patch.object(cloud_keys, 'get_key', side_effect=lambda name: None if name in cloud_keys.EXCLUDED else FAKE_KEY):
        for check in checks:
            with tempfile.TemporaryDirectory(prefix='kildall-cloud-') as temp:
                fixture = HTTPFixture()
                try:
                    check(Path(temp), fixture)
                except Exception as error:
                    failures.append(check.__name__)
                    print('FAIL:', check.__name__, type(error).__name__, flush=True)
                else:
                    print('PASS:', check.__name__, flush=True)
                finally:
                    fixture.close()
    assert not failures, 'Cloud checks failed: ' + ', '.join(failures)
    print(f'PASS: {len(checks)}/{len(checks)} cloud gate groups; localhost only', flush=True)


if __name__ == '__main__':
    main()
