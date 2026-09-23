"""Native stream boundaries must never return a partial or unvalidated tool call."""
import io
import json
from unittest.mock import patch

import orbi
import tool_runtime as runtime
from file_tools import TOOLS
from test_tool_grammar import call


def main():
    body = dict(messages=[dict(role='user', content='read')], tools=TOOLS,
                max_tokens=256, stream=True, temperature=0, tool_choice='auto')
    raw = '<|channel>thought\ninternal<channel|>Reading.\n' + call('read_file', dict(path='a.txt'))
    final = dict(stop=True, stop_type='eos', content='', timings=dict(predicted_n=20, predicted_ms=100, predicted_per_second=200))
    def response(text, finish=final):
        # Deliberately split every native marker, including inside a UTF-8 character.
        events = [dict(content=char, stop=False) for char in text]
        if finish is not None:
            events.append(finish)
        return io.BytesIO(b''.join(b'data: '+json.dumps(event).encode()+b'\n\n' for event in events))
    seen = []
    with patch.object(orbi, 'json_request', return_value={'prompt':'<|turn>user\nread<turn|>\n<|turn>model\n'}), patch.object(runtime._OPENER, 'open', return_value=response(raw)) as http:
        result = runtime.chat('http://127.0.0.1', body, on_text=seen.append)
        assert ''.join(seen) == result['choices'][0]['message']['content'] == 'Reading.\n'
        function = result['choices'][0]['message']['tool_calls'][0]['function']
        assert function['name'] == 'read_file' and json.loads(function['arguments']) == {'path':'a.txt'}
        request = json.loads(http.call_args.args[0].data)
        assert request['grammar'] and request['grammar_lazy'] and request['grammar_triggers'] == [{'type':1,'value':'<|tool_call>'},{'type':2,'value':r'<\|tool_call>'}]
    for text, finish in ((raw, None), (raw[:-4], dict(final, stop_type='limit')),
                         (raw.replace('read_file', 'sudo'), final),
                         (raw.replace('path:', 'missing:'), final),
                         (raw+call('read_file', dict(path='b.txt')), final)):
        with patch.object(orbi, 'json_request', return_value={'prompt':'<|turn>model\n'}), patch.object(runtime._OPENER, 'open', return_value=response(text, finish)):
            try:
                runtime.chat('http://127.0.0.1', body)
            except (ValueError, RuntimeError):
                pass
            else:
                raise AssertionError('Invalid or incomplete call returned to executor')
    for raw, expected in (('a < b', 'a < b'), ('hello<|channel>thought\nhidden', 'hello'), ('日本語', '日本語')):
        assert runtime.visible(raw, final=True) == expected
    with patch.object(orbi, 'json_request') as http:
        invalid = dict(type='function', function=dict(name='bad', parameters=dict(type='object', properties={}, additionalProperties=True)))
        try:
            runtime.prepare('http://127.0.0.1', dict(body, tools=[invalid]))
        except ValueError:
            pass
        else:
            raise AssertionError('Unsupported schema accepted')
        http.assert_not_called()
    print('PASS: per-request grammar, split stream markers, reasoning separation, unknown/malformed/multiple/truncated calls, premature EOF, fail-closed schemas')


if __name__ == '__main__':
    main()
