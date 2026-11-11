"""Project-relative search results and bounded tool replies; no inference."""
from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import re
import tempfile
import time
from unittest.mock import Mock, patch

import file_tools
import kildall


def request(endpoint, body=None, **kwargs):
    if endpoint.endswith('/slots'):
        return [dict(id=i, n_ctx=4096, is_processing=False) for i in range(3)]
    if endpoint.endswith('/apply-template'):
        return dict(prompt=json.dumps(body['messages']))
    assert endpoint.endswith('/tokenize')
    return dict(tokens=[1] * len(body['content'].encode()))


def relative_paths():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root/'nested/deep').mkdir(parents=True)
        (root/'nested/deep/a.py').write_text('needle = 1\n')
        found = file_tools.execute('glob_files', dict(path='nested', pattern='**/*.py'), root)
        assert found == dict(paths=['nested/deep/a.py'], truncated=False)
        found = file_tools.execute('grep_files', dict(path=str(root/'nested'), pattern='needle'), root)
        paths = [json.loads(line)['data']['path']['text'] for line in found['stdout'].splitlines()
                 if json.loads(line)['type'] == 'match']
        assert paths == ['nested/deep/a.py']
        # External reads remain allowed and still return project-relative names.
        found = file_tools.execute('glob_files', dict(path=str(root/'nested'), pattern='**/*.py'), root/'nested/deep')
        assert found['paths'] == ['a.py']


def large_result():
    config = kildall.settings()
    paths = [f'nested/{i:03d}-' + 'x'*100 + '.py' for i in range(200)]
    current = [dict(role='user', content='Find Python files.'),
               dict(role='assistant', content='', tool_calls=[dict(id='find', type='function',
                    function=dict(name='glob_files', arguments='{"path":".","pattern":"**/*.py"}'))]),
               dict(role='tool', tool_call_id='find', content=json.dumps(dict(paths=paths, truncated=False)))]
    original = copy.deepcopy(current)
    with patch.object(kildall, 'json_request', side_effect=request):
        fitted = kildall.fit_messages(config, kildall.system_prompt('.'), '', [], current)
    content, note = fitted[-1]['content'].rsplit('\n', 1)
    result = json.loads(content)
    assert result['paths'] and result['paths'] == paths[:len(result['paths'])]
    assert result['truncated'] is True
    assert note == f"{len(paths)-len(result['paths'])} items dropped; narrow the request."
    assert len(json.dumps(fitted).encode()) + 512 + 32 <= config['runtime']['context_size'] == 4096
    assert current == original and fitted[-1]['tool_call_id'] == 'find'
    assert fitted[-2] == current[-2]
    # Hook wrappers, grep JSONL and unsplittable binary output use the same cutter.
    wrapped = json.dumps(dict(result=dict(stdout='one\ntwo\nthree\nfour\n', exit_code=0)))
    reduced, count = kildall.trim_tool_result(wrapped)
    assert count == 2 and json.loads(reduced)['result'] == dict(stdout='one\ntwo\n', exit_code=0)
    reduced, count = kildall.trim_tool_result(json.dumps(dict(encoding='base64', data='YWJj'*100)))
    assert count == 1 and json.loads(reduced)['data'] == ''


def memory_before_tool_result():
    config = kildall.settings()
    recalled = 'The release coordinator is Imani Tran. ' * 12
    paths = [f'{i:03d}-' + 'x'*100 + '.py' for i in range(200)]
    current = [dict(role='user', content='Find Python files for the release coordinator.'),
               dict(role='assistant', content='', tool_calls=[dict(id='find', type='function',
                    function=dict(name='glob_files', arguments='{"path":".","pattern":"*.py"}'))]),
               dict(role='tool', tool_call_id='find', content=json.dumps(dict(paths=paths)))]
    original = copy.deepcopy(current)
    previous = [[dict(role='user', content='Old turn. ' * 500)]]
    with patch.object(kildall, 'json_request', side_effect=request):
        fitted = kildall.fit_messages(config, kildall.system_prompt('.'), recalled, previous, current)
    assert len(fitted) == 4  # Previous turns go first; recalled memory remains complete.
    assert fitted[1]['content'] == current[0]['content'] + '\n\n<memory>\n' + recalled + '\n</memory>'
    content, note = fitted[-1]['content'].rsplit('\n', 1)
    kept = json.loads(content)['paths']
    assert 0 < len(kept) < len(paths) and kept == paths[:len(kept)]
    assert note == f'{len(paths)-len(kept)} items dropped; narrow the request.'
    assert len(json.dumps(fitted).encode()) + 544 <= config['runtime']['context_size'] == 4096
    assert current == original


def turn_completes():
    with tempfile.TemporaryDirectory(dir=kildall.ROOT/'.session', prefix='result-context-test-') as directory:
        root = Path(directory)
        for i in range(100):
            (root/(f'{i:03d}-'+'x'*100+'.py')).write_text('pass\n')
        config = kildall.settings()
        config['cloud'] = dict(config.get('cloud', {}), enabled=False)
        config['paths'] = dict(config['paths'], db_path=root/'test.db')
        kildall.initialize(config['paths']['db_path'])
        with kildall.database(config['paths']['db_path']) as db:
            db.execute('INSERT INTO orbi_sessions VALUES(?,?,?)', ('bounded', str(root), time.time()))
        memory = Mock()
        memory.retrieve.return_value = dict(text='')
        seen = []
        def reply(config, messages, task, **kwargs):
            seen.append(messages)
            if len(seen) == 1:
                return dict(role='assistant', content='', tool_calls=[dict(id='find', type='function',
                    function=dict(name='glob_files', arguments='{"path":".","pattern":"*.py"}'))])
            assert re.search(r'\n\d+ items dropped; narrow the request\.$', messages[-1]['content'])
            assert len(json.dumps(messages).encode()) + 544 <= 4096
            return dict(role='assistant', content='I can narrow the pattern.')
        with patch.object(kildall, 'ensure_runtime'), \
             patch.object(kildall, 'json_request', side_effect=request), \
             patch.object(kildall, 'stream_reply', side_effect=reply), redirect_stdout(io.StringIO()):
            assert kildall.run_turn(config, memory, 'bounded', str(root), 'Find Python files.') == 0
        assert len(seen) == 2
        with kildall.database(config['paths']['db_path']) as db:
            assert db.execute('SELECT outcome FROM orbi_tasks').fetchone()[0] == 'done'
            stored = [json.loads(row[0]) for row in db.execute('SELECT payload FROM orbi_messages')]
        raw = next(message for message in stored if message['role'] == 'tool')
        assert len(json.loads(raw['content'])['paths']) == 100  # Raw audit evidence is preserved.


def compact_current_turn():
    config = kildall.settings()
    recalled = 'The release coordinator is Imani Tran.'
    current = [dict(role='user', content='Inspect the files and fix the release bug.')]
    for i in range(30):
        current += [dict(role='assistant', content='Inspecting the next file. ' * 30,
                         tool_calls=[dict(id=str(i), type='function', function=dict(
                             name='read_file', arguments=json.dumps(dict(path=f'{i}.py'))))]),
                    dict(role='tool', tool_call_id=str(i), content=json.dumps(
                        dict(text='1: first line\n2: second line\n', truncated=False)))]
    original = copy.deepcopy(current)
    def tokenize(endpoint, body, **kwargs):
        if endpoint.endswith('/tokenize'):
            return dict(tokens=[1] * ((len(body['content'].encode()) + 3) // 4))
        return request(endpoint, body, **kwargs)
    with patch.object(kildall, 'json_request', side_effect=tokenize):
        fitted = kildall.fit_messages(config, kildall.system_prompt('.'), recalled, [], current)
    assert (len(json.dumps(fitted).encode()) + 3) // 4 + 544 <= 4096
    assert fitted[1]['content'] == current[0]['content'] + '\n\n<memory>\n' + recalled + '\n</memory>'
    assert fitted[-8:] == current[-8:]  # Last four call/result pairs remain byte-for-byte complete.
    summaries = [m['content'] for m in fitted[2:] if m['role'] == 'assistant' and not m.get('tool_calls')]
    assert summaries and summaries == [f'read_file {i}.py: 2 lines read' for i in range(len(summaries))]
    assert current == original  # Compaction never changes stored audit evidence.


if __name__ == '__main__':
    for check in (relative_paths, large_result, memory_before_tool_result, turn_completes, compact_current_turn):
        check()
        print('PASS:', check.__name__, flush=True)
