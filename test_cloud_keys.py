"""Credential checks use fake values and mocked security; no real Keychain access."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

import cloud_keys as keys


def result(code=0, output=b'', error=b''):
    return subprocess.CompletedProcess(['/usr/bin/security'], code, output, error)


def main():
    fake = 'fake-import-value-$();"\\#'
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / 'keys.env'
        source.write_text("export OPENROUTER_API_KEY='" + fake + "' # literal\n"
                          'LLM7_API_KEY=\nGEMINI_API_KEY=excluded-one\n'
                          'GROQ_API_KEY=excluded-two\nGOOGLE_API_KEY=excluded-three\n')
        original = source.read_bytes()
        assert keys.parse_env(source)['OPENROUTER_API_KEY'] == fake
        with patch.object(keys.subprocess, 'run', side_effect=[result(), result(output=fake.encode() + b'\n')]) as run:
            captured = io.StringIO()
            with redirect_stdout(captured), redirect_stderr(captured):
                statuses = keys.import_keys(source)
            assert captured.getvalue() == ''
            assert statuses == [dict(name='OPENROUTER_API_KEY', status='verified'),
                                dict(name='LLM7_API_KEY', status='empty'),
                                dict(name='GEMINI_API_KEY', status='excluded'),
                                dict(name='GROQ_API_KEY', status='excluded'),
                                dict(name='GOOGLE_API_KEY', status='excluded')]
            write, read = run.call_args_list
            assert write.args[0] == ['/usr/bin/security', '-i', '-q']
            assert fake not in repr(write.args) and fake.encode().hex() not in repr(write.args)
            command = write.kwargs['input'].decode()
            assert command.count('\n') == 1 and f'-X {fake.encode().hex()} ' in command
            assert '-s kildall -a OPENROUTER_API_KEY' in command and '-U' in command
            assert '-A' not in command and '-v' not in write.args[0]
            assert read.args[0][-1] == str(keys.KEYCHAIN)
            assert write.kwargs['stderr'] == subprocess.PIPE
            assert write.kwargs['stdout'] == subprocess.PIPE
            assert write.kwargs['timeout'] == 30
        assert source.read_bytes() == original
        assert fake not in json.dumps(statuses)

        for bad in ('BAD-NAME=secret\n', 'A=one\nA=two\n', 'A="unterminated\n',
                    'A=secret\x00text\n', 'not an assignment\n', 'A=one two\n'):
            source.write_text(bad)
            with patch.object(keys.subprocess, 'run') as run:
                try:
                    keys.import_keys(source)
                    raise AssertionError('Invalid file imported')
                except ValueError as error:
                    assert 'secret' not in str(error)
                run.assert_not_called()

        source.write_text('A=literal#suffix # comment\nB="$(touch /not-executed)"\nC= # empty\n')
        assert keys.parse_env(source) == {'A': 'literal#suffix', 'B': '$(touch /not-executed)', 'C': ''}
        source.write_text('A=' + fake.encode().hex() + '\n')
        for responses in ([result(1, fake.encode(), fake.encode())], [result(), result(output=b'wrong\n')],
                          [result(), result(44)]):
            with patch.object(keys.subprocess, 'run', side_effect=responses):
                assert keys.import_keys(source) == [dict(name='A', status='failed')]
        source.write_text('A=' + 'x' * 2100 + '\n')
        with patch.object(keys.subprocess, 'run') as run:
            assert keys.import_keys(source) == [dict(name='A', status='failed')]
            run.assert_not_called()
        source.write_text('A=tiếng-Việt\n')
        with patch.object(keys.subprocess, 'run') as run:
            assert keys.import_keys(source) == [dict(name='A', status='failed')]
            run.assert_not_called()

    with patch.object(keys.subprocess, 'run') as run:
        for name in keys.EXCLUDED:
            assert keys.get_key(name) is None
        run.assert_not_called()
        for name in ('-a bad', 'A\nhelp', 'bad', '', None):
            try:
                keys.get_key(name)
                raise AssertionError('Invalid account accepted')
            except ValueError:
                pass
        run.assert_not_called()
    with patch.object(keys.subprocess, 'run', side_effect=[result(output=b'one\n'), result(output=b'two\n')]) as run:
        assert keys.get_key('A') == 'one' and keys.get_key('A') == 'two' and run.call_count == 2
    with patch.object(keys.subprocess, 'run', side_effect=[result(44), result(36), result(output=b'ok\n')]):
        assert keys.check_keys(['A', 'B', 'C', 'A', 'GROQ_API_KEY']) == [
            dict(name='A', status='missing'), dict(name='B', status='unreadable'),
            dict(name='C', status='available'), dict(name='GROQ_API_KEY', status='excluded')]
    with patch.object(keys, 'get_key', return_value=None) as get_key:
        assert len(keys.check_keys()) == len(keys.KNOWN_NAMES)
        assert {call.args[0] for call in get_key.call_args_list} == set(keys.KNOWN_NAMES) - keys.EXCLUDED
    for failure in (subprocess.TimeoutExpired(['/usr/bin/security'], 30, output=fake.encode()),
                    OSError(fake)):
        with patch.object(keys.subprocess, 'run', side_effect=failure):
            try:
                keys.get_key('A')
                raise AssertionError('Subprocess error ignored')
            except keys.KeychainError as error:
                assert fake not in str(error) and error.__suppress_context__

    google = 'AIza' + 'q' * 35
    groq = 'gsk_' + 'p' * 40
    data = {'messages': [{'content': f'{fake} / {google} / {groq} / API_KEY="opaque" / Bearer invisible'}],
            'api_key': 'also-invisible', 'count': 2, 'enabled': True}
    cleaned = keys.redact(data, [fake])
    encoded = json.dumps(cleaned)
    for secret in (fake, google, groq, 'opaque', 'invisible', 'also-invisible'):
        assert secret not in encoded
    assert cleaned['count'] == 2 and cleaned['enabled'] is True and data['api_key'] == 'also-invisible'
    assert keys.redact('a%2Fb + a/b', ['a/b']) == '[REDACTED] + [REDACTED]'
    assert keys.redact({'properties': {'api_key': {'type': 'string'}}}) == {'properties': {'api_key': {'type': 'string'}}}
    print('PASS: Keychain stdin/import verification, exclusions, literal parser, safe failures and secret scrub.')


if __name__ == '__main__':
    main()
