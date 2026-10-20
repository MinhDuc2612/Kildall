"""Prompt reuse, late memory and request telemetry; no model or live user data."""

from contextlib import redirect_stdout
import copy
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import time
from unittest.mock import Mock, patch

import benchmark
import kildall
import subagents
import tool_runtime


def context_checks(config):
    previous = [[dict(role='user', content=f'old-{n}'),
                 dict(role='assistant', content=f'answer-{n}')] for n in range(5)]
    current = [dict(role='user', content='Current question'),
               dict(role='assistant', content='', tool_calls=[dict(id='recall-1',
                    type='function', function=dict(name='recall', arguments='{}'))]),
               dict(role='tool', tool_call_id='recall-1', content='Retrieved data')]
    original = copy.deepcopy((previous, current))
    rendered = []
    token_count = lambda messages: 100

    def request(endpoint, body, **kwargs):
        if endpoint.endswith('/apply-template'):
            rendered.append(copy.deepcopy(body['messages']))
            return dict(prompt=json.dumps(body['messages']))
        assert endpoint.endswith('/tokenize')
        return dict(tokens=[1] * token_count(json.loads(body['content'])))

    with patch.object(kildall, 'json_request', side_effect=request):
        first = kildall.fit_messages(config, 'Stable system.', 'First memory.', previous, current)
        second = kildall.fit_messages(config, 'Stable system.', 'Updated memory.', previous, current)
        user_index = 1 + sum(map(len, previous))
        assert [i for i, pair in enumerate(zip(first, second)) if pair[0] != pair[1]] == [user_index]
        assert first[0]['content'] == 'Stable system.\n\n' + kildall.SYSTEM_RULES
        assert first[user_index]['content'] == 'Current question\n\n<memory>\nFirst memory.\n</memory>'
        assert second[user_index]['content'].count('<memory>') == 1
        assert (previous, current) == original

        rendered.clear()
        token_count = lambda messages: 3000 + 200 * sum(
            m.get('role') == 'user' and m.get('content', '').startswith('old-') for m in messages)
        fitted = kildall.fit_messages(config, 'Stable system.', 'Memory.', previous, current)
        assert len(rendered) == 2  # Five old turns become two in one removal.
        assert fitted[1:user_index - 6] == previous[3] + previous[4]
        assert token_count(fitted) <= 4096 - 544
        assert not any(m.get('content') in {'old-0', 'old-1', 'old-2'} for m in fitted)
        assert (previous, current) == original

        def memory_length(messages):
            return len(messages[-1]['content'].split('<memory>\n', 1)[1].split('\n</memory>', 1)[0])
        rendered.clear()
        token_count = lambda messages: 3553 if memory_length(messages) > 2 else 3552
        fitted = kildall.fit_messages(config, 'Stable system.', 'abcdefgh', [], current[:1])
        assert [memory_length(messages) for messages in rendered] == [8, 4, 2]
        assert token_count(fitted) == 4096 - 544
        rendered.clear()
        token_count = lambda messages: 3553
        try:
            kildall.fit_messages(config, 'Stable system.', 'abcdefgh', [], current[:1])
        except kildall.ContextOverflow as error:
            assert memory_length(error.messages) == 0
            assert 'Current question' in error.messages[-1]['content']
        else:
            raise AssertionError('Irreducible prompt was accepted')
        assert [memory_length(messages) for messages in rendered] == [8, 4, 2, 1, 0]
        assert (previous, current) == original


def runtime_checks(config, root):
    path = root / 'audit.db'
    assert kildall.cache_health(path) == 'Prompt cache: no request timings recorded'
    assert not path.exists()
    with sqlite3.connect(path):
        pass
    assert kildall.cache_health(path) == 'Prompt cache: no request timings recorded'
    kildall.initialize(path)
    assert kildall.cache_health(path) == 'Prompt cache: unavailable tokens reused (0/0 requests with timings)'
    with kildall.database(path) as db:
        db.execute('INSERT INTO orbi_sessions VALUES(?,?,?)', ('test', str(root), time.time()))
    config = copy.deepcopy(config)
    config['paths']['db_path'] = path
    parent = kildall.Task(path, 'test')
    child_task = None
    sent = []
    final = dict(content='Finished.', tokens=[1, 2], stop=True, stop_type='eos',
                 timings=dict(cache_n=100, prompt_n=25, predicted_n=2,
                              predicted_ms=20, predicted_per_second=100))

    def request(endpoint, body=None, **kwargs):
        if endpoint.endswith('/slots'):
            return [dict(id=i, n_ctx=4096, is_processing=False) for i in range(3)]
        if endpoint.endswith('/apply-template'):
            return dict(prompt='<|turn>user\n' + json.dumps(body['messages']) + '<turn|>\n<|turn>model\n')
        assert endpoint.endswith('/tokenize')
        return dict(tokens=[1])

    def opened(request, **kwargs):
        body = json.loads(request.data)
        sent.append(body)
        if request.full_url.endswith('/v1/chat/completions'):
            result = dict(choices=[dict(message=dict(role='assistant', content='Finished.'),
                                      finish_reason='stop')], timings=final['timings'])
        else:
            assert body['grammar'] and body['grammar_triggers']
            result = final
        encoded = json.dumps(result).encode()
        return io.BytesIO(b'data: ' + encoded + b'\n\n' if body['stream'] else encoded)

    try:
        parent.inference(None)
        parent.inference(dict(timings=dict(cache_n=0, prompt_n=0)))
        assert kildall.cache_health(path) == 'Prompt cache: unavailable tokens reused (1/2 requests with timings)'
        parent.inference(dict(timings=dict(cache_n=10)))
        for invalid in (-1, True, 1.5):
            try:
                parent.inference(dict(timings=dict(cache_n=invalid, prompt_n=1)))
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid cache count was persisted')

        prompt = dict(role='user', content='Original user request')
        parent.message(prompt)
        with patch.object(kildall, 'json_request', side_effect=request), \
                patch.object(tool_runtime._OPENER, 'open', side_effect=opened), \
                patch.object(subagents.Cancellation, 'open', side_effect=opened), \
                redirect_stdout(io.StringIO()):
            with subagents.bind_slot(kildall.url(config), 1, 3):
                messages = kildall.fit_messages(config, kildall.system_prompt(str(root)),
                                                'Parent retrieved fact', [], [prompt])
                assert kildall.stream_reply(config, messages, parent)['content'] == 'Finished.'
            assert sent[-1]['cache_prompt'] is True and sent[-1]['id_slot'] == 1
            child_task = kildall.Task(path, 'test', parent=dict(parent_task=parent.id,
                parent_decision='test-decision', project=str(root), tools=[], requested=[], mode='shared'))
            child_messages = [dict(role='user', content='Child request')]
            child_task.message(child_messages[0])
            child = dict(task=child_task, config=config, slot=2, memory='Child retrieved fact',
                         messages=child_messages, timings=[])
            manager = subagents.Manager(config, Mock(), parent, str(root), kildall.BASE_TOOLS)
            assert manager.infer(child, subagents.Cancellation())['content'] == 'Finished.'
            assert sent[-1]['cache_prompt'] is True and sent[-1]['id_slot'] == 2
            assert child['timings'][0]['cache_n'] == 100 and child['timings'][0]['prompt_n'] == 25
            assert child_messages == [dict(role='user', content='Child request')]

            # Benchmarks retain their uncached request policy, with and without tools.
            with subagents.bind_slot(kildall.url(config), 1, 3), \
                    patch('urllib.request.urlopen', side_effect=opened):
                for options in ({}, {'tools': kildall.BASE_TOOLS}):
                    benchmark.chat(kildall.url(config), [prompt], **options)
                    assert sent[-1]['cache_prompt'] is False and sent[-1]['id_slot'] == 1
            with subagents.bind_slot(kildall.url(config), 1, 3), \
                    patch.object(tool_runtime._OPENER, 'open', side_effect=RuntimeError('test transport failure')):
                try:
                    kildall.stream_reply(config, messages, parent)
                except RuntimeError as error:
                    assert str(error) == 'test transport failure'
                else:
                    raise AssertionError('Transport failure was hidden')

        assert kildall.cache_health(path) == 'Prompt cache: 80.00% tokens reused (3/6 requests with timings)'
        with kildall.database(path) as db:
            rows = [dict(row) for row in db.execute('SELECT * FROM orbi_inference ORDER BY id')]
            stored = [json.loads(row[0]) for row in db.execute('SELECT payload FROM orbi_messages')]
        assert [(row['task'], row['slot'], row['cache_n'], row['prompt_n']) for row in rows[3:5]] == [
            (parent.id, 1, 100, 25), (child_task.id, 2, 100, 25)]
        assert rows[-1]['cache_n'] is None and rows[-1]['prompt_n'] is None
        assert not any('<memory>' in json.dumps(message) for message in stored)
    finally:
        if child_task is not None:
            child_task.finish('done')
        parent.finish('done')
    history = kildall.history(path, 'test')
    assert len(history) == 1 and history[0][0] == prompt
    assert not any('<memory>' in json.dumps(turn) for turn in history)
    assert not any('Child request' in json.dumps(turn) for turn in history)


def main():
    config = kildall.settings()
    config['runtime'] = dict(config['runtime'], context_size=4096, parallel=3)
    context_checks(config)
    with tempfile.TemporaryDirectory(prefix='prompt-reuse-test-') as temporary:
        runtime_checks(config, Path(temporary))
    print('PASS: late copied memory, unchanged history, chunked turn trimming, overflow; '
          'parent/child cache and pinned slots through native grammar; request telemetry, '
          'unknown/zero health counts, transport failure recording; benchmarks stay uncached.')


if __name__ == '__main__':
    main()
