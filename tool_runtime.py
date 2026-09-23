"""Schema GBNF on native Gemma 4 completions, using the server's unchanged template."""

import json
import math
import urllib.request
import uuid

from tool_grammar import TOOL_START, TOOL_END, parse_tool_call, tool_grammar

# Match common_chat_params_init_gemma4 in the pinned b10809 runtime.
PRESERVED = ['<|channel>', '<channel|>', TOOL_START, TOOL_END, '<|turn>']
_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def visible(raw, *, final=False):
    """Separate content from native thought/control frames and a pending tool call."""
    content, position = [], 0
    prefix = '<|turn>model\n'
    if raw.startswith(prefix):
        position = len(prefix)
    elif prefix.startswith(raw) and not final:
        return ''
    while position < len(raw):
        start = raw.find('<', position)
        if start < 0:
            content.append(raw[position:])
            break
        content.append(raw[position:start])
        rest = raw[start:]
        if rest.startswith(TOOL_START):
            break
        if rest.startswith('<|channel>thought'):
            end = raw.find('<channel|>', start + len('<|channel>thought'))
            if end < 0:
                break
            position = end + len('<channel|>')
        elif rest.startswith('<channel|>'):
            position = start + len('<channel|>')
        elif not final and any(marker.startswith(rest) for marker in
                               (TOOL_START, '<|channel>thought', '<channel|>', prefix)):
            break
        else:
            content.append('<')
            position = start + 1
    return ''.join(content)


def prepare(endpoint, body):
    from orbi import json_request
    if body.get('parallel_tool_calls', False) or body.get('tool_choice', 'auto') not in ('auto', 'required'):
        raise ValueError('Expected single-call auto or required tool choice')
    if any(key in body for key in ('grammar', 'response_format')):
        raise ValueError('Tool schema is the sole grammar source')
    tools = body['tools']
    grammar = tool_grammar(tools)  # Fail before any request if a schema is unsupported.
    rendered = json_request(endpoint + '/apply-template', {
        'messages': body['messages'], 'tools': tools,
        'tool_choice': body.get('tool_choice', 'auto'), 'parallel_tool_calls': False,
        'add_generation_prompt': True})['prompt']
    if not isinstance(rendered, str) or '<|turn>' not in rendered:
        raise ValueError('Expected the pinned Gemma 4 native chat template')
    native = {key: body[key] for key in ('temperature', 'top_p', 'samplers', 'seed', 'cache_prompt') if key in body}
    native.update(prompt=rendered, n_predict=body['max_tokens'], stream=body.get('stream', False),
                  grammar=grammar, grammar_lazy=body.get('tool_choice', 'auto') == 'auto',
                  # WORD becomes a special-token trigger; PATTERN also catches ordinary-token spellings.
                  grammar_triggers=[{'type': 1, 'value': TOOL_START}, {'type': 2, 'value': r'<\|tool_call>'}],
                  preserved_tokens=PRESERVED, return_tokens=True)
    return native


def chat(endpoint, body, *, on_text=None):
    """Return the existing callable JSON protocol; no fallback to unconstrained tools."""
    from orbi import strict_json
    native = prepare(endpoint, body)
    request = urllib.request.Request(endpoint + '/completion', json.dumps(native).encode(),
                                     {'Content-Type': 'application/json'})
    raw, shown, tokens, completed = '', '', [], None
    with _OPENER.open(request, timeout=180) as response:
        if native['stream']:
            for line in response:
                if len(line) > 1_000_000:
                    raise ValueError('Oversized native stream event')
                if not line.startswith(b'data:'):
                    continue
                data = line[5:].strip()
                if data == b'[DONE]':
                    break
                event = strict_json(data)
                if 'error' in event:
                    raise RuntimeError(str(event['error']))
                text = event.get('content', '')
                if not isinstance(text, str):
                    raise ValueError('Invalid native stream content')
                raw += text
                tokens.extend(event.get('tokens', []))
                if len(raw) > 1_000_000:
                    raise ValueError('Oversized native response')
                current = visible(raw)
                if not current.startswith(shown):
                    raise ValueError('Native content changed after delivery')
                if on_text and current != shown:
                    on_text(current[len(shown):])
                shown = current
                if event.get('stop') is True:
                    completed = event
                    break
        else:
            data = response.read(2_000_001)
            if len(data) > 2_000_000:
                raise ValueError('Oversized native response')
            completed = strict_json(data)
            if 'error' in completed:
                raise RuntimeError(str(completed['error']))
            raw = completed.get('content')
            tokens = completed.get('tokens', [])
    if not completed or completed.get('stop') is not True or not isinstance(raw, str):
        raise RuntimeError('Native completion ended without a completed response')
    stop = completed.get('stop_type')
    if stop not in ('eos', 'limit', 'word'):
        raise ValueError('Unknown native stop reason')
    content = visible(raw, final=True)
    if not content.startswith(shown):
        raise ValueError('Final native content changed after delivery')
    if on_text and content != shown:
        on_text(content[len(shown):])
    message = dict(role='assistant', content=content)
    finish = 'length' if stop == 'limit' else 'stop'
    if TOOL_START in raw:
        if stop == 'limit':
            raise ValueError('Truncated tool call; no execution')
        call = parse_tool_call(raw[raw.index(TOOL_START):], body['tools'])
        message['tool_calls'] = [dict(id='call_' + uuid.uuid4().hex, type='function',
            function=dict(name=call['name'], arguments=json.dumps(call['arguments'], ensure_ascii=False, allow_nan=False)))]
        finish = 'tool_calls'
    elif body.get('tool_choice') == 'required':
        raise ValueError('Required tool call missing')
    timing = completed.get('timings', {})
    for key in ('predicted_n', 'predicted_ms', 'predicted_per_second'):
        value = timing.get(key, 0)
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError('Invalid native generation timing')
    return dict(choices=[dict(message=message, finish_reason=finish)], timings=timing,
                request=body, native_request=native,
                native_response=dict(content=raw, tokens=tokens, stop_type=stop,
                                     generation_settings=completed.get("generation_settings")))
