"""Real temporary commits; no real key changes and no credential output."""
from contextlib import redirect_stderr
import io
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
import uuid

import secret_scanner as scanner


def main():
    with tempfile.TemporaryDirectory(prefix='kildall-secret-controls-', dir=scanner.ROOT / '.session') as directory:
        temporary = Path(directory).resolve()
        repo = temporary / 'repo'
        repo.mkdir()

        def git(*arguments, success=True):
            result = subprocess.run([scanner.GIT, '-C', str(repo), *arguments],
                                    capture_output=True, timeout=30)
            if success and result.returncode:
                raise AssertionError('Temporary git command failed; output withheld')
            return result

        git('init', '-q')
        git('config', 'user.name', 'Scanner Test')
        git('config', 'user.email', 'scanner@example.invalid')
        git('config', 'commit.gpgsign', 'false')
        env_value = ('private-' + uuid.uuid4().hex).encode()
        keychain_value = ('credential-' + uuid.uuid4().hex).encode()
        source, stored = temporary / 'keys.env', temporary / 'keychain-fixture'
        source.write_bytes(b'PLANTED_API_KEY=' + env_value + b'\nEMPTY=\n')
        stored.write_bytes(keychain_value)
        wrapper = temporary / 'hook.py'
        wrapper.write_text('from pathlib import Path\nimport sys\n'
            f'sys.path.insert(0, {str(scanner.ROOT)!r})\nfrom secret_scanner import run\n'
            f'raise SystemExit(run(source=Path({str(source)!r}), '
            f'keychain_reader=lambda: [Path({str(stored)!r}).read_bytes()]))\n')
        hooks = scanner.install((repo,), scanner=wrapper, interpreter=Path(sys.executable))
        assert scanner.install((repo,), scanner=wrapper, interpreter=Path(sys.executable)) == hooks
        clean = repo / 'clean.txt'
        clean.write_text('A clean first commit. A task-with-a-long-description is ordinary text.\n')
        git('add', '.')
        git('commit', '-qm', 'clean fixture')
        cases = [(prefix.encode() + uuid.uuid4().hex.encode(), rule) for prefix, rule in (
            ('sk-', 'openai-pattern'), ('gsk_', 'groq-pattern'), ('AIza', 'google-pattern'),
            ('nvapi-', 'nvidia-pattern'), ('hf_', 'huggingface-pattern'))]
        cases.extend([(env_value, 'keys.env-value'), (keychain_value, 'keychain-value')])
        for value, rule in cases:
            file = repo / 'candidate.bin'
            # The secret crosses a read boundary and lives in a binary blob.
            file.write_bytes(b'\x00' * (1024 * 1024 - 3) + value + b'\x00')
            git('add', 'candidate.bin')
            file.write_text('clean working tree does not change staged bytes')
            result = git('commit', '-qm', 'must be refused', success=False)
            captured = result.stdout + result.stderr
            assert result.returncode != 0 and rule.encode() in captured
            assert all(secret not in captured for secret, _ in cases)
            git('reset', '-q', 'HEAD', '--', 'candidate.bin')
            file.unlink()
        # All proposed blobs are scanned, including unchanged staged files.
        clean.write_bytes(b'prefix ' + env_value)
        git('add', 'clean.txt')
        git('-c', 'core.hooksPath=/dev/null', 'commit', '-qm', 'contained historical fixture')
        another = repo / 'another.txt'
        another.write_text('clean change')
        git('add', 'another.txt')
        result = git('commit', '-qm', 'historical secret still refused', success=False)
        assert result.returncode != 0 and env_value not in result.stdout + result.stderr
        clean.write_text('clean again')
        git('add', 'clean.txt')
        git('commit', '-qm', 'clean tree allowed')
        # Even credential-bearing filenames and errors cannot disclose a value.
        leaked_name = repo / env_value.decode()
        leaked_name.write_bytes(env_value)
        git('add', '--', leaked_name.name)
        output = io.StringIO()
        with redirect_stderr(output):
            assert scanner.run(repo, source=source, keychain_reader=lambda: [keychain_value]) == 1
        assert env_value.decode() not in output.getvalue() and '[REDACTED]' in output.getvalue()
        git('reset', '-q', 'HEAD', '--', leaked_name.name)
        leaked_name.unlink()
        for reader, env in ((lambda: [], temporary / 'missing.env'),
                            (lambda: (_ for _ in ()).throw(RuntimeError(env_value.decode())), source)):
            output = io.StringIO()
            with redirect_stderr(output):
                assert scanner.run(repo, source=env, keychain_reader=reader) == 1
            assert env_value.decode() not in output.getvalue()
        # Account enumeration does not apply cloud-provider exclusions; values
        # are read by security, never passed to security as arguments.
        with patch.object(scanner, '_keychain_accounts', return_value=[('fixture.keychain', 'GEMINI_API_KEY')]), \
             patch.object(scanner, '_security', return_value=subprocess.CompletedProcess([], 0, keychain_value + b'\n', b'')) as security:
            assert scanner.keychain_values() == [keychain_value]
            assert security.call_args.args[0] == ['find-generic-password', '-s', 'kildall', '-a', 'GEMINI_API_KEY', '-w', 'fixture.keychain']
        with patch.object(scanner, '_keychain_accounts', return_value=[('fixture.keychain', 'ANY_NAME')]), \
             patch.object(scanner, '_security', return_value=subprocess.CompletedProcess([], 44, b'', env_value)):
            try:
                scanner.keychain_values()
            except scanner.ScanError as error:
                assert str(error) == 'keychain-read'
            else:
                raise AssertionError('Failed Keychain read was allowed')
        # The product deliberately disables arbitrary Git hooks. Its shared
        # commit boundary must still scan the immutable approved index.
        import kildall
        import permissions
        database = temporary / 'controls.db'
        kildall.initialize(database)
        original_scan = scanner.scan
        def private_scan(repository, **kwargs):
            return original_scan(repository, source=source, keychain_reader=lambda: [], **kwargs)
        clean.write_bytes(env_value)
        git('add', 'clean.txt')
        head = git('rev-parse', 'HEAD').stdout
        with patch.object(scanner, 'ROOT', repo), patch.object(scanner, 'scan', side_effect=private_scan), \
                patch.object(permissions, 'terminal_confirm', side_effect=AssertionError('Secret diff must not be displayed')):
            try:
                permissions.run_action(database, str(repo), 'commit', dict(path=str(repo), message='refuse secret'))
            except PermissionError as error:
                assert 'keys.env-value' in str(error) and env_value.decode() not in str(error)
            else:
                raise AssertionError('Closed executor bypassed the scanner')
        assert git('rev-parse', 'HEAD').stdout == head
        clean.write_text('clean executor commit')
        git('add', 'clean.txt')
        hooks[0].write_text('#!/bin/sh\nexit 23\n')
        with patch.object(scanner, 'ROOT', repo), patch.object(scanner, 'scan', side_effect=private_scan), \
                patch.object(permissions, 'terminal_confirm', return_value=True):
            result = permissions.run_action(database, str(repo), 'commit', dict(path=str(repo), message='verified clean commit'))
        assert result['commit'].encode() == git('rev-parse', 'HEAD').stdout.strip()
        assert git('rev-parse', 'HEAD').stdout != head
        hook = hooks[0]
        hook.write_text('#!/bin/sh\nexit 23\n')
        saved = hook.read_bytes()
        try:
            scanner.install((repo,), scanner=wrapper, interpreter=Path(sys.executable))
        except scanner.ScanError:
            pass
        else:
            raise AssertionError('Custom hook overwritten')
        assert hook.read_bytes() == saved
    print('PASS: five patterns, planted keys.env and Keychain values block real commits; '
          'clean commits allowed; staged/full-tree/binary/boundary scanning; '
          'redacted filenames, fail-closed reads, excluded-provider enumeration, safe installer; '
          'closed executor scans the approved index without running arbitrary hooks')


if __name__ == '__main__':
    main()
