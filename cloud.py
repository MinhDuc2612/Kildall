"""Necessary-only free cloud fallback; no grammar, no permission bypass."""

import datetime
import email.utils
import hashlib
import json
import math
import re
import time
import urllib.error
import urllib.request
import uuid

from tool_grammar import validate_arguments

# Verified free-access paths. Config can narrow these, never authorize paid IDs.
PROVIDERS = {
    'llm7': ('https://api.llm7.io/v1', 'LLM7_API_KEY', {'codestral-latest'}),
    'ovh': ('https://oai.endpoints.kepler.ai.cloud.ovh.net/v1', '', {'gpt-oss-20b'}),
    'openrouter': ('https://openrouter.ai/api/v1', 'OPENROUTER_API_KEY', {
        'nvidia/nemotron-3-super-120b-a12b:free', 'nvidia/nemotron-3-ultra-550b-a55b:free',
        'poolside/laguna-s-2.1:free', 'cohere/north-mini-code:free'}),
}
EXHAUSTED = 'cloud exhausted — answering locally'


def credential_names(path, configured=()):
    from cloud_keys import KNOWN_NAMES
    from kildall import database
    with database(path) as db:
        db.execute('CREATE TABLE IF NOT EXISTS cloud_accounts(name TEXT PRIMARY KEY)')
        imported = [row[0] for row in db.execute('SELECT name FROM cloud_accounts ORDER BY name')]
    return tuple(dict.fromkeys([*KNOWN_NAMES, *imported, *configured]))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # Never forward credentials to a redirected endpoint.


def providers(config):
    cloud = config.get('cloud', {})
    if not cloud.get('enabled', False):
        return {}
    result = cloud.get('providers', {})
    if not isinstance(result, dict):
        raise ValueError('Cloud providers must be an ordered table')
    for name, item in result.items():
        if name not in PROVIDERS:
            raise ValueError('Cloud provider is not authorized')
        base, key, models = PROVIDERS[name]
        if (type(item.get('keyless', not bool(key))) is not bool
                or (item.get('keyless', False) and name not in ('llm7', 'ovh'))):
            raise ValueError('Anonymous access is not authorized for this provider')
        allowed = item.get('allowed_models')
        if (item.get('base_url') != base or item.get('key_name') != key
                or not isinstance(allowed, list) or not allowed
                or any(type(model) is not str or model not in models for model in allowed)):
            raise ValueError('Cloud endpoint, key account or exact free model is not authorized')
        for field in ('daily_requests', 'daily_tokens', 'requests_per_minute', 'requests_per_hour'):
            if type(item.get(field, 0)) is not int or item.get(field, 0) < 0:
                raise ValueError('Cloud limits must be nonnegative integers (0 means undocumented)')
        if (type(item.get('min_interval_seconds', 0)) not in (int, float)
                or not math.isfinite(item.get('min_interval_seconds', 0))
                or item.get('min_interval_seconds', 0) < 0
                or item.get('quota_window', 'utc_day') not in ('utc_day', 'rolling_24h')):
            raise ValueError('Cloud quota interval/window invalid')
        if (type(item.get('context_tokens')) is not int or item['context_tokens'] < 1024
                or item.get('limits_status') != 'unverified'
                or item.get('trains_on_data') not in (True, False, 'unknown')):
            raise ValueError('Cloud context, quota provenance or data policy missing')
    return result


def decode(text):
    """Reject duplicate fields and nonfinite numbers before a schema sees them."""
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON field')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Nonfinite JSON number')
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)


def validate_message(response, tools):
    """Validate before persistence or executor admission; do not repair any call."""
    try:
        choices = response['choices']
        if not isinstance(choices, list) or len(choices) != 1:
            raise ValueError()
        message = choices[0]['message']
        if message.get('role') != 'assistant' or choices[0].get('finish_reason') not in ('stop', 'tool_calls'):
            raise ValueError()
        content = message.get('content')
        if content is not None and type(content) is not str:
            raise ValueError()
        calls = message.get('tool_calls', [])
        if calls is None:
            calls = []  # OpenAI-compatible nullable field: no tool call was emitted.
        if not isinstance(calls, list) or len(calls) > 1:
            raise ValueError()
        if calls:
            call = calls[0]
            if set(call) != {'id', 'type', 'function'} or call['type'] != 'function':
                raise ValueError()
            if not isinstance(call['id'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', call['id']):
                raise ValueError()
            function = call['function']
            if set(function) != {'name', 'arguments'} or type(function['arguments']) is not str:
                raise ValueError()
            schema = next(t['function']['parameters'] for t in tools if t['function']['name'] == function['name'])
            validate_arguments(schema, decode(function['arguments']))
        elif not content or choices[0]['finish_reason'] == 'tool_calls':
            raise ValueError()
        return dict(role='assistant', content=content or '', **({'tool_calls': calls} if calls else {}))
    except (KeyError, IndexError, AttributeError, TypeError, ValueError, StopIteration):
        raise ValueError('Cloud response rejected: malformed message or tool call') from None


def retry_after(value, now):
    try:
        delay = float(value)
        if math.isfinite(delay):
            return max(1, delay)
    except (TypeError, ValueError):
        pass
    try:
        return max(1, email.utils.parsedate_to_datetime(value).timestamp() - now)
    except (TypeError, ValueError, OverflowError):
        return 60


class Client:
    def __init__(self, config):
        from kildall import database
        self.providers = providers(config)
        self.path = config['paths']['db_path']
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        with database(self.path) as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS cloud_state(provider TEXT PRIMARY KEY,
                    cooldown REAL NOT NULL DEFAULT 0, invalid_hash TEXT,
                    disabled INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS cloud_requests(id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL, task TEXT, created REAL NOT NULL,
                    tokens INTEGER NOT NULL, status TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS cloud_usage ON cloud_requests(provider,created);
            ''')

    def reserve(self, name, item, fingerprint, tokens, task):
        from kildall import database
        now = time.time()
        with database(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('INSERT OR IGNORE INTO cloud_state(provider) VALUES(?)', (name,))
            state = db.execute('SELECT * FROM cloud_state WHERE provider=?', (name,)).fetchone()
            if state['disabled'] or state['cooldown'] > now or state['invalid_hash'] == fingerprint:
                return None
            start = (now - 86400 if item.get('quota_window') == 'rolling_24h' else
                     datetime.datetime.fromtimestamp(now, datetime.timezone.utc).replace(
                         hour=0, minute=0, second=0, microsecond=0).timestamp())
            used = db.execute('SELECT count(*),coalesce(sum(tokens),0) FROM cloud_requests '
                              'WHERE provider=? AND created>=?', (name, start)).fetchone()
            for field, total in [('daily_requests', used[0] + 1), ('daily_tokens', used[1] + tokens)]:
                if item.get(field, 0) and total > item[field] * 9 // 10:
                    return None
            for field, seconds in [('requests_per_minute', 60), ('requests_per_hour', 3600)]:
                count = db.execute('SELECT count(*) FROM cloud_requests WHERE provider=? AND created>?',
                                   (name, now - seconds)).fetchone()[0]
                if item.get(field, 0) and count >= item[field]:
                    return None
            latest = db.execute('SELECT max(created) FROM cloud_requests WHERE provider=?', (name,)).fetchone()[0]
            if latest and item.get('min_interval_seconds', 0) and now - latest < item['min_interval_seconds']:
                return None
            request_id = uuid.uuid4().hex
            # Reserve before dispatch; a crash/timeout keeps the conservative debit.
            db.execute('INSERT INTO cloud_requests VALUES(?,?,?,?,?,?)',
                       (request_id, name, task, now, tokens, 'reserved'))
            db.execute('UPDATE cloud_state SET invalid_hash=NULL WHERE provider=?', (name,))
            return request_id

    def finish(self, request_id, name, status, *, tokens=None, cooldown=0, invalid_hash=None, disabled=False):
        from kildall import database
        with database(self.path) as db:
            db.execute('UPDATE cloud_requests SET status=?,tokens=coalesce(?,tokens) WHERE id=?',
                       (status, tokens, request_id))
            db.execute('UPDATE cloud_state SET cooldown=max(cooldown,?),invalid_hash=?, '
                       'disabled=max(disabled,?) WHERE provider=?',
                       (cooldown, invalid_hash, int(disabled), name))

    def enable(self, name):
        from kildall import database
        if name not in self.providers:
            raise ValueError('Unknown configured provider')
        with database(self.path) as db:
            db.execute('UPDATE cloud_state SET disabled=0 WHERE provider=?', (name,))

    def reply(self, messages, tools, task=None):
        from cloud_keys import KeychainError, get_key, redact
        # Read all eligible secrets at call time, so a prompt cannot leak another
        # configured provider's key. Excluded key formats are scrubbed by redact.
        try:
            accounts = credential_names(self.path, (p['key_name'] for p in self.providers.values() if p['key_name']))
            credentials = {account: get_key(account) for account in accounts}
            keys = {name: (credentials[item['key_name']] or '') if item['key_name'] else ''
                    for name, item in self.providers.items()}
        except KeychainError:
            return None  # Cannot safely scrub unknown credentials; stay local.
        secrets = tuple(key for key in credentials.values() if key)
        for name, item in self.providers.items():
            key = keys[name]
            if item['key_name'] and not key and not item.get('keyless', False):
                continue
            body = redact(dict(model=item['allowed_models'][0], messages=messages, tools=tools,
                               tool_choice='auto', parallel_tool_calls=False,
                               temperature=0, max_tokens=512, stream=False), secrets)
            if not tools:
                for field in ('tools', 'tool_choice', 'parallel_tool_calls'):
                    body.pop(field)
            encoded = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
            # ponytail: conservative UTF-8 upper bound; provider tokenizers can
            # replace this if rejected long inputs become a measured limitation.
            reserve = len(encoded) + 1024 + 512
            if reserve > item['context_tokens']:
                continue
            fingerprint = hashlib.sha256(key.encode()).hexdigest()
            request_id = self.reserve(name, item, fingerprint, reserve, task)
            if request_id is None:
                continue
            headers = {'Content-Type': 'application/json', 'User-Agent': 'Kildall/0.1'}
            if key:
                headers['Authorization'] = 'Bearer ' + key
            request = urllib.request.Request(item['base_url'] + '/chat/completions', encoded, headers)
            response_headers = {}
            try:
                try:
                    with self.opener.open(request, timeout=30) as response:
                        status, response_headers = response.status, response.headers
                        raw = response.read(1_048_577)
                except urllib.error.HTTPError as error:
                    status, response_headers = error.code, error.headers
                    raw = error.read(1_048_577)
                    error.close()
                if len(raw) > 1_048_576:
                    raise ValueError('Cloud response exceeds size limit')
                try:
                    result = decode(raw.decode())
                except (ValueError, UnicodeError):
                    result = {}
                error_text = (json.dumps(result['error'], ensure_ascii=True) if isinstance(result, dict) and result.get('error')
                              else raw.decode(errors='replace') if status != 200 or not isinstance(result, dict)
                              or not result.get('choices') else '').lower()
                billed = (isinstance(result, dict) and isinstance(result.get('usage'), dict)
                          and any(isinstance(result['usage'].get(k), (int, float)) and result['usage'][k] > 0
                                  for k in ('cost', 'cost_usd')))
                billing = status == 402 or billed or bool(re.search(
                    r'bill|payment|credit|paid|balance|insufficient.fund|spending|purchase', error_text))
                if billing:
                    self.finish(request_id, name, 'billing_disabled', disabled=True)
                    continue
                if status in (401, 403):
                    self.finish(request_id, name, 'key_invalid', invalid_hash=fingerprint)
                    continue
                if status == 429 or 500 <= status <= 599:
                    self.finish(request_id, name, 'cooldown', cooldown=time.time() + retry_after(
                        response_headers.get('Retry-After'), time.time()))
                    continue
                if status != 200 or not isinstance(result, dict) or result.get('error'):
                    self.finish(request_id, name, 'http_rejected', cooldown=time.time() + 60)
                    continue
                usage = result.get('usage', {}).get('total_tokens') if isinstance(result.get('usage', {}), dict) else None
                usage = usage if type(usage) is int and usage > 0 else None
                try:
                    message = validate_message(result, tools)
                    scrubbed = redact(message, secrets)
                    if scrubbed.get('tool_calls') != message.get('tool_calls'):
                        raise ValueError('Credential-bearing tool call rejected without repair')
                    message = scrubbed
                except ValueError:
                    self.finish(request_id, name, 'malformed_rejected', tokens=usage)
                    raise
                self.finish(request_id, name, 'answered', tokens=usage)
                return message
            except (TimeoutError, urllib.error.URLError, OSError):
                self.finish(request_id, name, 'transport_cooldown', cooldown=time.time() + 60)
            except ValueError:
                self.finish(request_id, name, 'malformed_rejected')
                raise ValueError('Cloud response rejected: malformed message or tool call') from None
        return None
