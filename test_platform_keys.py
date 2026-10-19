"""Golden Mac credential calls and fail-closed non-Mac dispatch; fake values only."""
import ast
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

import cloud_keys
import secret_scanner
from kildall_platform import UnsupportedPlatform, darwin_keys, system


BASE = '29ab89bd6a1c7fbe097a3e781de779ffc2b66d17'


def original(name):
    source = subprocess.run([system().executable('git'), 'show', f'{BASE}:{name}.py'],
                            capture_output=True, check=True).stdout.decode()
    module = types.ModuleType('before_' + name)
    module.__file__ = str(Path(__file__).with_name(name + '.py'))
    exec(compile(source, module.__file__, 'exec'), module.__dict__)
    return module, source


def result(code=0, output=b''):
    return subprocess.CompletedProcess([], code, output, b'private error withheld')


def capture(call, responses):
    output = io.StringIO()
    with patch.object(subprocess, 'run', side_effect=responses) as run, \
            redirect_stdout(output), redirect_stderr(output):
        try:
            observed = ('result', call())
        except Exception as error:
            observed = ('error', type(error).__name__, str(error))
    assert output.getvalue() == ''
    return observed, run.call_args_list


def main():
    with patch.object(sys, 'platform', 'darwin'):
        before, _ = original('cloud_keys')
        with patch.dict(sys.modules, cloud_keys=before):
            before_scanner, scanner_source = original('secret_scanner')
        for name, responses in (
            ('A', [result(output=b'private-value\n')]), ('A', [result(44)]),
            ('A', [result(36)]), ('A', [result(output=b'\xff')]),
            ('A', [result(output=b'bad\x00text')]),
            ('A', [subprocess.TimeoutExpired('security', 30)]),
            ('A', [OSError('private error withheld')]),
            ('GROQ_API_KEY', []), ('bad-name', []),
        ):
            assert capture(lambda: before.get_key(name), responses) == capture(
                lambda: cloud_keys.get_key(name), responses)
        with tempfile.TemporaryDirectory(prefix='kildall-platform-keys-') as directory:
            path = Path(directory) / 'credentials.env'
            for text, responses in (
                ('A=private-value\nGROQ_API_KEY=excluded\nB=\n', [result(), result(output=b'private-value\n')]),
                ('A=private-value\n', [result(1)]),
                ('A=private-value\n', [result(), result(output=b'mismatch\n')]),
                ('A=private-value\n', [result(), result(44)]),
                ('A=tiếng-Việt\n', []), ('A=' + 'x' * 2100 + '\n', []),
                ('A=one\nA=two\n', []), ('', []), ('GEMINI_API_KEY=excluded\n', []),
            ):
                path.write_text(text)
                assert capture(lambda: before.import_keys(path), responses) == capture(
                    lambda: cloud_keys.import_keys(path), responses)
                assert path.read_text() == text
        names = ['A', 'B', 'C', 'A', 'GROQ_API_KEY']
        responses = [result(44), result(36), result(output=b'private-value\n')]
        assert capture(lambda: before.check_keys(names), responses) == capture(
            lambda: cloud_keys.check_keys(names), responses)
        for response in (result(output=b'private-value\n'), result(output=b'616263\n'), result(44)):
            accounts = [('fixture.keychain', 'GROQ_API_KEY')]
            with patch.object(before_scanner, '_keychain_accounts', return_value=accounts):
                expected = capture(before_scanner.keychain_values, [response])
            with patch.object(darwin_keys, 'accounts', return_value=accounts):
                actual = capture(secret_scanner.keychain_values, [response])
            assert actual == expected
        # The framework enumeration body is moved unchanged, including cleanup.
        old = next(node for node in ast.parse(scanner_source).body
                   if isinstance(node, ast.FunctionDef) and node.name == '_keychain_accounts')
        old.name = 'accounts'
        for node in ast.walk(old):
            if isinstance(node, ast.Name) and node.id == 'ScanError':
                node.id = 'KeychainError'
        current = next(node for node in ast.parse(Path(darwin_keys.__file__).read_text()).body
                       if isinstance(node, ast.FunctionDef) and node.name == 'accounts')
        assert ast.dump(old) == ast.dump(current)

    for platform in ('linux', 'win32'):
        with patch.object(sys, 'platform', platform), \
                patch.object(cloud_keys, 'parse_env', side_effect=AssertionError('env read forbidden')) as env, \
                patch.object(subprocess, 'run', side_effect=AssertionError('command forbidden')) as run:
            for call in (lambda: cloud_keys.get_key('A'), lambda: cloud_keys.get_key('GROQ_API_KEY'),
                         lambda: cloud_keys.import_keys(), lambda: cloud_keys.check_keys([]),
                         lambda: cloud_keys.check_keys(['GROQ_API_KEY']),
                         secret_scanner.keychain_values, lambda: secret_scanner.scan(Path.cwd()),
                         lambda: secret_scanner.install(())):
                try:
                    call()
                except UnsupportedPlatform as error:
                    assert 'not implemented' in str(error).lower()
                else:
                    raise AssertionError('Unsupported credential store was allowed')
            output = io.StringIO()
            with redirect_stderr(output):
                assert secret_scanner.run() == 1
            assert 'not implemented' in output.getvalue()
            env.assert_not_called()
            run.assert_not_called()
    print('PASS: golden Keychain argv/stdin/results/errors and scanner reads match 29ab89b; '
          'Linux/Windows keys refuse before file reads or commands.')


if __name__ == '__main__':
    main()
