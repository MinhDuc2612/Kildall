"""Context allocation and streamed progress must preserve admission and grammar."""
import contextlib
import io
import json
from unittest.mock import patch

import kildall
import subagents
import tool_runtime


def main():
    config = dict(runtime=dict(context_size=16384, parallel=3, kv_unified=True,
                               router_reserve_tokens=4096, port=19200))
    assert kildall.context_flags(config) == ['-c', '36864', '-kvu', '--kv-unified-per-slot', '16384', '--no-cache-idle-slots']
    config['runtime']['kv_unified'] = False
    assert kildall.context_flags(config) == ['-c', '49152']
    for value in (True, 16383, 262400, 0):
        with patch.dict(config['runtime'], context_size=value):
            try:
                kildall.context_flags(config)
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid context accepted')
    with patch.object(kildall, 'json_request', return_value=[dict(id=1, n_ctx=4096, is_processing=False)]):
        try:
            subagents.wait_idle(config, 1)
        except RuntimeError:
            pass
        else:
            raise AssertionError('Smaller server slot accepted')
    with patch.object(kildall, 'json_request', return_value=[dict(id=1, n_ctx=16384, is_processing=False)]):
        subagents.wait_idle(config, 1)
    assert '16,384' in str(kildall.ContextOverflow([], 16384))
    output = io.StringIO()
    progress = dict(total=8192, processed=1024, cache=0, time_ms=12000)
    with contextlib.redirect_stderr(output):
        kildall.read_progress(config)(progress)
    assert '1,024/8,192' in output.getvalue() and '84s remaining' in output.getvalue()
    body = dict(messages=[dict(role='user', content='hi')], tools=kildall.BASE_TOOLS,
                max_tokens=32, stream=True, temperature=0)
    final = dict(stop=True, stop_type='eos', content='hello', timings=dict(predicted_n=1,
                 predicted_ms=100, predicted_per_second=10))
    def response(p):
        return io.BytesIO(b''.join(b'data: '+json.dumps(row).encode()+b'\n\n'
            for row in (dict(prompt_progress=p), final)))
    seen = []
    with subagents.bind_slot('http://127.0.0.1', 1, 3), \
         patch.object(kildall, 'json_request', return_value=dict(prompt='<|turn>model\n')), \
         patch.object(tool_runtime._OPENER, 'open', return_value=response(progress)) as http:
        result = tool_runtime.chat('http://127.0.0.1', body, on_progress=seen.append, timeout=470)
        request = json.loads(http.call_args.args[0].data)
        assert request['grammar'] and request['return_progress'] and request['id_slot'] == 1
        assert seen == [progress] and result['choices'][0]['message']['content'] == 'hello'
        assert http.call_args.kwargs['timeout'] == 470
    with subagents.bind_slot('http://127.0.0.1', 1, 3), \
         patch.object(kildall, 'json_request', return_value=dict(prompt='<|turn>model\n')), \
         patch.object(tool_runtime._OPENER, 'open', return_value=response(dict(progress, total=-1))):
        try:
            tool_runtime.chat('http://127.0.0.1', body, on_progress=seen.append)
        except ValueError:
            pass
        else:
            raise AssertionError('Malformed progress accepted')
    print('PASS: context layout/validation, undersized slot refusal, overflow limit, progress/ETA, unchanged grammar, malformed progress refusal')


if __name__ == '__main__':
    main()
