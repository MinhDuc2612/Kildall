"""Login-Keychain credentials and secret scrubbing; never display credential values."""
import hashlib
import hmac
import json
from pathlib import Path
import re
import shlex
import subprocess
from urllib.parse import quote, quote_plus


DEFAULT_SOURCE = Path.home() / '.config/orbi/keys.env'
KEYCHAIN = Path.home() / 'Library/Keychains/login.keychain-db'
EXCLUDED = frozenset({'GEMINI_API_KEY', 'GOOGLE_API_KEY', 'GROQ_API_KEY'})
KNOWN_NAMES = ('GEMINI_API_KEY', 'GROQ_API_KEY', 'GOOGLE_API_KEY', 'OPENROUTER_API_KEY',
               'MISTRAL_API_KEY', 'COHERE_API_KEY', 'HF_TOKEN', 'CLOUDFLARE_API_TOKEN',
               'CLOUDFLARE_ACCOUNT_ID', 'OLLAMA_API_KEY', 'AIONLABS_API_KEY',
               'KILOCODE_API_KEY', 'LLM7_API_KEY', 'NVIDIA_API_KEY', 'MODELSCOPE_API_KEY',
               'SILICONFLOW_API_KEY', 'ZAI_API_KEY', 'CEREBRAS_API_KEY', 'OPENCODE_API_KEY')
REDACTED = '[REDACTED]'
_NAME = re.compile(r'[A-Z][A-Z0-9_]{0,127}\Z')
_TOKEN = re.compile(r'(?<![\w-])(?:AIza[\w-]{20,}|gsk_[\w-]{12,}|sk-[\w-]{12,}|hf_[\w-]{12,}|nvapi-[\w-]{12,}|csk-[\w-]{12,})')
_BEARER = re.compile(r'(?i)(\bbearer\s+)[^\s\x22\x27<>]+')
_ASSIGNMENT = re.compile(r'(?i)(\b(?:[a-z][a-z0-9_-]*(?:key|token|secret)|api[_-]?key|authorization)\b[\x22\x27]?\s*[:=]\s*)(?:\x22[^\x22\r\n]*\x22|\x27[^\x27\r\n]*\x27|[^\s,;\x22\x27}]+)')
_SECRET_FIELD = re.compile(r'(?i)(?:[a-z][a-z0-9_-]*(?:key|token|secret)|api[_-]?key|authorization)\Z')


class KeychainError(RuntimeError):
    """Deliberately contains no subprocess output or credential-bearing command."""


def _name(name):
    if not isinstance(name, str) or not _NAME.fullmatch(name):
        raise ValueError('Invalid credential variable name')
    return name


def parse_env(path=DEFAULT_SOURCE):
    """Read dotenv assignments as literal data. Returned values must stay private."""
    try:
        with Path(path).expanduser().open('rb') as stream:
            raw = stream.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError
        text = raw.decode('utf-8-sig')
        values = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:].lstrip()
            name, separator, value = line.partition('=')
            name = _name(name.strip())
            if not separator or name in values:
                raise ValueError
            value = value.strip()
            if value.startswith(('"', "'")):
                parts = shlex.split(value, comments=True, posix=True)
                if len(parts) != 1:
                    raise ValueError
                value = parts[0]
            else:
                value = '' if value.startswith('#') else re.split(r'\s+#', value, maxsplit=1)[0].strip()
                if any(char.isspace() for char in value):
                    raise ValueError
            if any(ord(char) < 32 or ord(char) == 127 for char in value):
                raise ValueError
            values[name] = value
        return values
    except (OSError, UnicodeError, ValueError):
        raise ValueError('Cannot read credential file: expected unique literal NAME=value assignments') from None


def _security(arguments, *, input=None):
    try:
        return subprocess.run(['/usr/bin/security', *arguments], input=input,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        raise KeychainError('Keychain operation failed') from None


def get_key(name):
    """Read at call time; None means absent or excluded, never an unreadable item."""
    name = _name(name)
    if name in EXCLUDED:
        return None
    result = _security(['find-generic-password', '-s', 'kildall', '-a', name,
                        '-w', str(KEYCHAIN)])
    if result.returncode == 44:  # errSecItemNotFound (-25300), shell exit status.
        return None
    if result.returncode:
        raise KeychainError('Keychain credential is unreadable')
    try:
        value = result.stdout.removesuffix(b'\n').decode('utf-8')
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise ValueError
    except (UnicodeError, ValueError):
        raise KeychainError('Keychain credential is unreadable') from None
    return value or None


def import_keys(path=DEFAULT_SOURCE):
    """Import without deleting the source; every result contains only name/status."""
    statuses = []
    values = parse_env(path)  # Validate the whole file before any mutation.
    for name, value in values.items():
        status = 'excluded' if name in EXCLUDED else 'empty' if not value else None
        if status is None:
            try:
                # security -w hex-encodes non-printable bytes without a marker.
                # API credentials must round-trip unambiguously as printable ASCII.
                if not value.isascii():
                    raise KeychainError('Credential must be printable ASCII')
                keychain = str(KEYCHAIN)
                if any(ord(char) < 32 or ord(char) == 127 for char in keychain):
                    raise KeychainError('Invalid login Keychain path')
                # security's interactive parser is not a shell: quote one whole arg.
                keychain = '"' + keychain.replace('\\', '\\\\').replace('"', '\\"') + '"'
                command = f'add-generic-password -U -s kildall -a {name} -X {value.encode().hex()} {keychain}\n'
                # Apple's security.c bounds an interactive input line at 4096 bytes.
                if len(command.encode()) >= 4096:
                    raise KeychainError('Credential exceeds Keychain import limit')
                result = _security(['-i', '-q'], input=command.encode())
                if result.returncode:
                    raise KeychainError('Keychain import failed')
                restored = get_key(name)
                if restored is None or not hmac.compare_digest(
                        hashlib.sha256(value.encode()).digest(), hashlib.sha256(restored.encode()).digest()):
                    raise KeychainError('Keychain verification failed')
                status = 'verified'
            except KeychainError:
                status = 'failed'
        statuses.append(dict(name=name, status=status))
    return statuses


def check_keys(names=KNOWN_NAMES):
    """Report storage availability only, not API validity; never read the env file."""
    statuses = []
    for name in dict.fromkeys(names):
        name = _name(name)
        try:
            status = 'excluded' if name in EXCLUDED else 'available' if get_key(name) else 'missing'
        except KeychainError:
            status = 'unreadable'
        statuses.append(dict(name=name, status=status))
    return statuses


def redact(value, secrets=()):
    """Scrub exact credentials and common credential syntax in a JSON value."""
    variants = set()
    for secret in secrets:
        if secret:
            variants.update((secret, quote(secret, safe=''), quote_plus(secret),
                             json.dumps(secret, ensure_ascii=True)[1:-1]))
    exact = sorted(variants, key=len, reverse=True)

    def clean(item):
        if isinstance(item, str):
            for secret in exact:
                item = item.replace(secret, REDACTED)
            item = _TOKEN.sub(REDACTED, item)
            item = _BEARER.sub(lambda match: match[1] + REDACTED, item)
            return _ASSIGNMENT.sub(lambda match: match[1] + REDACTED, item)
        if isinstance(item, dict):
            return {clean(key): REDACTED if isinstance(key, str) and _SECRET_FIELD.fullmatch(key)
                    and isinstance(entry, str) else clean(entry) for key, entry in item.items()}
        if isinstance(item, (list, tuple)):
            return [clean(entry) for entry in item]
        return item

    return clean(value)
