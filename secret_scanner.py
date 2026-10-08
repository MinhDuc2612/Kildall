"""Fail-closed pre-commit checks of the proposed tree; credentials never leave memory."""
import argparse
import ctypes as ct
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

from cloud_keys import DEFAULT_SOURCE, _security, parse_env


ROOT = Path(__file__).resolve().parent
GIT = '/opt/homebrew/bin/git'
PATTERNS = tuple((name, re.compile(rb'(?<![A-Za-z0-9_-])' + pattern)) for name, pattern in (
    ('openai-pattern', rb'sk-[A-Za-z0-9_-]{12,}'),
    ('groq-pattern', rb'gsk_[A-Za-z0-9_-]{12,}'),
    ('google-pattern', rb'AIza[A-Za-z0-9_-]{20,}'),
    ('nvidia-pattern', rb'nvapi-[A-Za-z0-9_-]{12,}'),
    ('huggingface-pattern', rb'hf_[A-Za-z0-9_-]{12,}'),
))


class ScanError(RuntimeError):
    """Only fixed messages, never subprocess output or credential values."""


def _keychain_accounts():
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
            raise ScanError('keychain-read')
        service = cf.CFStringCreateWithCString(None, b'kildall', 0x08000100)
        if not service:
            raise ScanError('keychain-read')
        for index in range(cf.CFArrayGetCount(search)):
            keychain = cf.CFArrayGetValueAtIndex(search, index)
            buffer, length = ct.create_string_buffer(4096), ct.c_uint32(4096)
            if sec.SecKeychainGetPath(keychain, ct.byref(length), buffer):
                raise ScanError('keychain-read')
            path = os.fsdecode(buffer.raw[:length.value])
            query, selected, found = None, None, p()
            try:
                selected = cf.CFArrayCreate(None, (p * 1)(keychain), 1, None)
                query = cf.CFDictionaryCreateMutable(None, 0, None, None)
                if not selected or not query:
                    raise ScanError('keychain-read')
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
                    raise ScanError('keychain-read')
                for item in range(cf.CFArrayGetCount(found)):
                    attributes = cf.CFArrayGetValueAtIndex(found, item)
                    account = cf.CFDictionaryGetValue(attributes, constant('kSecAttrAccount'))
                    if not account:
                        yield path, ''
                        continue
                    size = cf.CFStringGetMaximumSizeForEncoding(cf.CFStringGetLength(account), 0x08000100) + 1
                    text = ct.create_string_buffer(size)
                    if not cf.CFStringGetCString(account, text, size, 0x08000100):
                        raise ScanError('keychain-read')
                    yield path, text.value.decode('utf-8')
            finally:
                for value in (found.value, query, selected):
                    if value:
                        cf.CFRelease(value)
    finally:
        for value in (service, search.value):
            if value:
                cf.CFRelease(value)


def keychain_values():
    values = []
    try:
        for path, account in _keychain_accounts():
            result = _security(['find-generic-password', '-s', 'kildall', '-a', account, '-w', path])
            if result.returncode:
                raise ScanError('keychain-read')
            value = result.stdout.removesuffix(b'\n')
            if value:
                values.append(value)
                # security -w renders non-printable passwords as unmarked hex.
                # Checking both interpretations also protects literal hex keys.
                if re.fullmatch(rb'(?:[0-9A-Fa-f]{2})+', value):
                    values.append(bytes.fromhex(value.decode('ascii')))
    except Exception:
        raise ScanError('keychain-read') from None
    return values


def _git(repo, *arguments):
    try:
        result = subprocess.run([GIT, '-C', str(repo), *arguments], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError):
        raise ScanError('git-read') from None
    if result.returncode:
        raise ScanError('git-read')
    return result.stdout


def scan(repo, *, source=DEFAULT_SOURCE, keychain_reader=keychain_values, git_reader=_git):
    try:
        secrets = [(value.encode(), 'keys.env-value') for value in parse_env(source).values() if value]
    except Exception:
        raise ScanError('keys.env-read') from None
    try:
        secrets += [(value, 'keychain-value') for value in keychain_reader() if value]
    except Exception:
        raise ScanError('keychain-read') from None
    findings = []
    for entry in git_reader(repo, 'ls-files', '--stage', '-z').split(b'\0'):
        if not entry:
            continue
        metadata, path = entry.split(b'\t', 1)
        mode, oid, stage = metadata.split()
        if stage != b'0':
            raise ScanError('unmerged-index')
        if mode == b'160000':  # A gitlink stores an object ID, not file contents.
            continue
        if not re.fullmatch(rb'[0-9a-f]{40,64}', oid):
            raise ScanError('git-read')
        # ponytail: one staged blob in RAM; stream if tracked artifacts grow.
        data = git_reader(repo, 'cat-file', 'blob', oid.decode('ascii'))
        rules = {rule for value, rule in secrets if value in data}
        rules.update(rule for rule, pattern in PATTERNS if pattern.search(data))
        if rules:
            # Filenames are untrusted too: never echo a credential or terminal control.
            for value, _ in sorted(secrets, key=lambda item: len(item[0]), reverse=True):
                path = path.replace(value, b'[REDACTED]')
            for _, pattern in PATTERNS:
                path = pattern.sub(b'[REDACTED]', path)
            safe_path = ascii(os.fsdecode(path))
            findings.extend((safe_path, rule) for rule in sorted(rules))
    return findings


def enforce_commit(repo, index):
    """Protect our two repos when the closed executor bypasses arbitrary hooks."""
    if repo not in (ROOT, ROOT.parent):
        return
    from permissions import git
    try:
        findings = scan(repo, git_reader=lambda repository, *args: git(repository, *args, index=index))
    except Exception:
        raise PermissionError('Secret scanner could not verify the approved index') from None
    if findings:
        raise PermissionError('; '.join(f'{path}: {rule}' for path, rule in findings))


def run(repo=None, **kwargs):
    try:
        findings = scan(Path.cwd() if repo is None else repo, **kwargs)
        for path, rule in findings:
            print(f'{path}: {rule}', file=sys.stderr)
        return int(bool(findings))
    except Exception as error:
        rule = str(error) if isinstance(error, ScanError) else 'scanner-error'
        print(f'<index>: {rule}', file=sys.stderr)
        return 1


def install(repositories=(ROOT, ROOT.parent), *, scanner=Path(__file__).resolve(), interpreter=ROOT / '.venv/bin/python'):
    content = ('#!/bin/sh\n# kildall-secret-scanner v1\nexec ' + shlex.quote(str(interpreter))
               + ' ' + shlex.quote(str(scanner)) + '\n').encode()
    paths = []
    for repo in repositories:
        configured = subprocess.run([GIT, '-C', str(repo), 'config', '--get', 'core.hooksPath'],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if configured.returncode not in (0, 1) or configured.stdout.strip():
            raise ScanError('custom-hooks-path')
        directory = Path(os.fsdecode(_git(repo, 'rev-parse', '--git-common-dir').strip()))
        if not directory.is_absolute():
            directory = Path(repo) / directory
        path = directory / 'hooks/pre-commit'
        if path.is_symlink() or path.parent.is_symlink():
            raise ScanError('custom-hook')
        if path.exists() and path.read_bytes() != content:
            raise ScanError('custom-hook')
        paths.append(path)
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            descriptor, temporary = tempfile.mkstemp(prefix='.kildall-hook-', dir=path.parent)
            try:
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(content)
                    stream.flush()
                    os.fchmod(stream.fileno(), 0o755)
                os.link(temporary, path)  # Exclusive publish never overwrites a custom hook.
            finally:
                Path(temporary).unlink()
        path.chmod(0o755)
        if path.read_bytes() != content or not os.access(path, os.X_OK):
            raise ScanError('hook-install')
    return paths


def main():
    parser = argparse.ArgumentParser(description='Check staged files for secrets without displaying values.')
    parser.add_argument('--install', action='store_true', help='install pre-commit checks in the code and vault repositories')
    arguments = parser.parse_args()
    if not arguments.install:
        return run()
    try:
        for path in install():
            print(f'{path}: installed')
        return 0
    except Exception:
        print('<hook>: installation-refused', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
