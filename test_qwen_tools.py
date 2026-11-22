"""Qwen XML tool calls (Swift-1.5-Qwen3.8-27B): real b10809 GBNF, strict parser, runtime dispatch.

Run: .venv/bin/python test_qwen_tools.py   (no model is allocated)
"""
import io
import json
from unittest.mock import patch

import kildall
import subagents
import tool_runtime as runtime
from test_tool_grammar import NativeGrammar, rejects
from tool_grammar import parse_qwen_tool_call, qwen_tool_grammar

TOOLS = kildall.TOOLS + [subagents.TOOL]
PROMPT = ('<|im_start|>system\n# Tools\n<tool_call>\n<function=example>\n<|im_end|>\n'
          '<|im_start|>user\nread<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n')


def render(name, arguments):
    """Same text the Swift chat template renders for a past call."""
    parts = [f'<parameter={k}>\n{v if isinstance(v, str) else json.dumps(v)}\n</parameter>\n'
             for k, v in arguments.items()]
    return f'<tool_call>\n<function={name}>\n' + ''.join(parts) + '</function>\n</tool_call>'


GOOD = [
    ('read_file', {'path': 'a.txt'}),
    ('read_file', {'max_lines': 5, 'path': 'dir/b c.txt', 'start_line': 1}),
    ('remember', {'text': 'multi\nline </param> <parameter=x>', 'scope': 'project', 'tier': 'L1'}),
    ('run_command', {'command': 'ls -la', 'timeout': 3600}),
    ('write', {'path': 'x.py', 'content': ''}),
    ('spawn_agents', {'tasks': [{'prompt': 'a "quoted"\\ é', 'mode': 'shared'}, {'prompt': 'b'}]}),
]
BAD = [
    '<tool_call>\n<function=read_file>\n</function>\n</tool_call>',  # missing required path
    render('read_file', {'path': 'a', 'nope': 1}),
    render('read_file', {'path': 'a', 'max_lines': 201}),
    render('read_file', {'path': 'a', 'max_lines': 'five'}),
    render('remember', {'text': 't', 'scope': 'galaxy', 'tier': 'L1'}),
    render('sudo', {'command': 'x'}),
    render('spawn_agents', {'tasks': []}),
    render('spawn_agents', {'tasks': [{'prompt': 'a', 'extra': 1}]}),
    render('read_file', {'path': 'a'}).replace('</tool_call>', '</tool_call>x'),
    render('read_file', {'path': 'a'}).replace('<parameter=path>\na', '<parameter=path>\na\n</parameter>\n<parameter=path>\nb'),
]


def main():
    native = NativeGrammar()
    grammar = qwen_tool_grammar(TOOLS)
    for name, arguments in GOOD:
        text = render(name, arguments)
        assert native.matches(grammar, text), text
        assert parse_qwen_tool_call(text, TOOLS) == {'name': name, 'arguments': arguments}, text
    for text in BAD:
        assert not native.matches(grammar, text), text
        rejects(parse_qwen_tool_call, text, TOOLS)
    for text in (render('read_file', {'path': 'a'}) + render('read_file', {'path': 'b'}),
                 render('spawn_agents', {'tasks': [{'prompt': 'a'}]}).replace('"a"}', '"a", "prompt": "b"}'),
                 render('read_file', {'path': 'a', 'max_lines': 5}).replace('\n5\n', '\nNaN\n')):
        rejects(parse_qwen_tool_call, text, TOOLS)
    # Grammar and parser both stop the raw string at the first delimiter.
    assert not native.matches(grammar, render('read_file', {'path': 'a\n</parameter>\nb'}))
    rejects(qwen_tool_grammar, [{'type': 'function', 'function': {'name': 'f', 'parameters': {
        'type': 'object', 'properties': {'x': {'type': ['string', 'null']}}, 'additionalProperties': False}}}])

    assert runtime.qwen_visible('Reading.\n<tool') == 'Reading.\n'
    assert runtime.qwen_visible('Reading.\n<tool', final=True) == 'Reading.\n<tool'
    assert runtime.qwen_visible('a <b>\n' + render('read_file', {'path': 'a'})) == 'a <b>\n'

    body = dict(messages=[dict(role='user', content='read')], tools=TOOLS, max_tokens=256,
                stream=True, temperature=0, tool_choice='auto')
    final = dict(stop=True, stop_type='eos', content='', timings=dict(predicted_n=20, predicted_ms=100, predicted_per_second=200))
    def response(text, finish=final):
        events = [dict(content=char, stop=False) for char in text] + ([finish] if finish else [])
        return io.BytesIO(b''.join(b'data: ' + json.dumps(e).encode() + b'\n\n' for e in events))
    raw = 'Reading.\n\n' + render('read_file', {'path': 'a.txt'})
    seen = []
    with patch.object(kildall, 'json_request', return_value={'prompt': PROMPT}), \
         patch.object(runtime._OPENER, 'open', return_value=response(raw)) as http:
        result = runtime.chat('http://127.0.0.1', body, on_text=seen.append)
        message = result['choices'][0]['message']
        assert ''.join(seen) == message['content'] == 'Reading.\n\n'
        assert result['choices'][0]['finish_reason'] == 'tool_calls'
        assert json.loads(message['tool_calls'][0]['function']['arguments']) == {'path': 'a.txt'}
        request = json.loads(http.call_args.args[0].data)
        assert request['grammar'] == grammar and request['grammar_lazy']
        assert request['grammar_triggers'] == [{'type': 1, 'value': '<tool_call>'}, {'type': 2, 'value': '<tool_call>'}]
        assert request['preserved_tokens'] == ['<tool_call>', '</tool_call>']
    for text, finish in ((raw[:-5], dict(final, stop_type='limit')), (raw.replace('read_file', 'sudo'), final)):
        with patch.object(kildall, 'json_request', return_value={'prompt': PROMPT}), \
             patch.object(runtime._OPENER, 'open', return_value=response(text, finish)):
            rejects(runtime.chat, 'http://127.0.0.1', body)
    for prompt in (PROMPT.replace('<think>\n\n</think>\n\n', '<think>\n'), PROMPT.replace('<function=', '<fn=')):
        with patch.object(kildall, 'json_request', return_value={'prompt': prompt}):
            rejects(runtime.prepare, 'http://127.0.0.1', body)
    print(f'PASS: Qwen XML tool calls, {native.checks} real b10809 grammar checks, strict parser, runtime dispatch')


if __name__ == '__main__':
    from subagents import bind_slot
    with bind_slot('http://127.0.0.1', 0, 1):
        main()
