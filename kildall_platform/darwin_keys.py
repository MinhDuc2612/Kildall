"""macOS login Keychain operations; credentials never enter argv or errors."""
import ctypes as ct
import hashlib
import hmac
import os
from pathlib import Path
import re
import subprocess

from cloud_keys import KeychainError


KEYCHAIN = Path.home() / 'Library/Keychains/login.keychain-db'


def security(arguments, *, input=None):
    try:
        return subprocess.run(['/usr/bin/security', *arguments], input=input,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        raise KeychainError('Keychain operation failed') from None


def get_key(name):
    """Read at call time; None means absent, never an unreadable item."""
    result = security(['find-generic-password', '-s', 'kildall', '-a', name,
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


def put_key(name, value):
    """Store through security stdin and verify the exact read-back hash."""
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
    result = security(['-i', '-q'], input=command.encode())
    if result.returncode:
        raise KeychainError('Keychain import failed')
    restored = get_key(name)
    if restored is None or not hmac.compare_digest(
            hashlib.sha256(value.encode()).digest(), hashlib.sha256(restored.encode()).digest()):
        raise KeychainError('Keychain verification failed')


def accounts():
    """Enumerate metadata only, including excluded providers and arbitrary accounts.

    macOS SDK SecItem.h documents kSecMatchLimitAll + kSecReturnAttributes;
    SecKeychain.h documents CopySearchList/GetPath. Password reads remain in
    /usr/bin/security, which owns the ACL access granted by keys import.
    """
    cf = ct.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
    sec = ct.CDLL('/System/Library/Frameworks/Security.framework/Security')
    p, n = ct.c_void_p, ct.c_long
    for library, name, result, arguments in (
        (cf, 'CFArrayGetCount', n, [p]),
        (cf, 'CFArrayGetValueAtIndex', p, [p, n]),
        (cf, 'CFArrayCreate', p, [p, ct.POINTER(p), n, p]),
        (cf, 'CFDictionaryCreateMutable', p, [p, n, p, p]),
        (cf, 'CFDictionarySetValue', None, [p, p, p]),
        (cf, 'CFDictionaryGetValue', p, [p, p]),
        (cf, 'CFStringCreateWithCString', p, [p, ct.c_char_p, ct.c_uint32]),
        (cf, 'CFStringGetLength', n, [p]),
        (cf, 'CFStringGetMaximumSizeForEncoding', n, [n, ct.c_uint32]),
        (cf, 'CFStringGetCString', ct.c_bool, [p, ct.c_char_p, n, ct.c_uint32]),
        (cf, 'CFRelease', None, [p]),
        (sec, 'SecKeychainCopySearchList', ct.c_int32, [ct.POINTER(p)]),
        (sec, 'SecKeychainGetPath', ct.c_int32, [p, ct.POINTER(ct.c_uint32), ct.c_char_p]),
        (sec, 'SecItemCopyMatching', ct.c_int32, [p, ct.POINTER(p)]),
    ):
        function = getattr(library, name)
        function.restype, function.argtypes = result, arguments

    def constant(name):
        return p.in_dll(cf if name.startswith('kCF') else sec, name).value

    search, service = p(), None
    try:
        if sec.SecKeychainCopySearchList(ct.byref(search)) or not search.value:
            raise KeychainError('keychain-read')
        service = cf.CFStringCreateWithCString(None, b'kildall', 0x08000100)
        if not service:
            raise KeychainError('keychain-read')
        for index in range(cf.CFArrayGetCount(search)):
            keychain = cf.CFArrayGetValueAtIndex(search, index)
            buffer, length = ct.create_string_buffer(4096), ct.c_uint32(4096)
            if sec.SecKeychainGetPath(keychain, ct.byref(length), buffer):
                raise KeychainError('keychain-read')
            path = os.fsdecode(buffer.raw[:length.value])
            query, selected, found = None, None, p()
            try:
                selected = cf.CFArrayCreate(None, (p * 1)(keychain), 1, None)
                query = cf.CFDictionaryCreateMutable(None, 0, None, None)
                if not selected or not query:
                    raise KeychainError('keychain-read')
                for key, value in (
                    ('kSecClass', constant('kSecClassGenericPassword')),
                    ('kSecAttrService', service),
                    ('kSecMatchSearchList', selected),
                    ('kSecMatchLimit', constant('kSecMatchLimitAll')),
                    ('kSecReturnAttributes', constant('kCFBooleanTrue')),
                ):
                    cf.CFDictionarySetValue(query, constant(key), value)
                status = sec.SecItemCopyMatching(query, ct.byref(found))
                if status == -25300:  # errSecItemNotFound: empty is explicit.
                    continue
                if status or not found.value:
                    raise KeychainError('keychain-read')
                for item in range(cf.CFArrayGetCount(found)):
                    attributes = cf.CFArrayGetValueAtIndex(found, item)
                    account = cf.CFDictionaryGetValue(attributes, constant('kSecAttrAccount'))
                    if not account:
                        yield path, ''
                        continue
                    size = cf.CFStringGetMaximumSizeForEncoding(cf.CFStringGetLength(account), 0x08000100) + 1
                    text = ct.create_string_buffer(size)
                    if not cf.CFStringGetCString(account, text, size, 0x08000100):
                        raise KeychainError('keychain-read')
                    yield path, text.value.decode('utf-8')
            finally:
                for value in (found.value, query, selected):
                    if value:
                        cf.CFRelease(value)
    finally:
        for value in (service, search.value):
            if value:
                cf.CFRelease(value)


def values():
    values = []
    try:
        for path, account in accounts():
            result = security(['find-generic-password', '-s', 'kildall', '-a', account, '-w', path])
            if result.returncode:
                raise KeychainError('keychain-read')
            value = result.stdout.removesuffix(b'\n')
            if value:
                values.append(value)
                # security -w renders non-printable passwords as unmarked hex.
                # Checking both interpretations also protects literal hex keys.
                if re.fullmatch(rb'(?:[0-9A-Fa-f]{2})+', value):
                    values.append(bytes.fromhex(value.decode('ascii')))
    except Exception:
        raise KeychainError('keychain-read') from None
    return values

