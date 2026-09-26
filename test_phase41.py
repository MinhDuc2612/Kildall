"""All ten file and six shell checks through the sole permission executor."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

import kildall
import permissions as p
from shell_tools import run_bounded


def pdf(path):
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
        b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 500 500] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
        b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
    stream = b'BT /F1 24 Tf 20 450 Td (ORBI PDF CONTENT) Tj ET'
    objects.append(b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream')
    data, offsets = b'%PDF-1.4\n', [0]
    for i, body in enumerate(objects, 1):
        offsets.append(len(data))
        data += str(i).encode()+b' 0 obj\n'+body+b'\nendobj\n'
    xref = len(data)
    data += b'xref\n0 6\n0000000000 65535 f \n'+b''.join(f'{n:010d} 00000 n \n'.encode() for n in offsets[1:])
    data += b'trailer << /Size 6 /Root 1 0 R >>\nstartxref\n'+str(xref).encode()+b'\n%%EOF\n'
    path.write_bytes(data)


def main():
    checks = []
    def passed(label):
        checks.append(label)
        print('PASS:', label, flush=True)
    with tempfile.TemporaryDirectory(dir=kildall.ROOT / '.session', prefix='phase41-') as temporary:
        work = Path(temporary)
        db = work / 'audit.db'
        kildall.initialize(db)
        def run(operation, **args):
            return p.run_action(db, str(work), operation, args)
        def rejected(operation, **args):
            try:
                run(operation, **args)
            except (PermissionError, ValueError, OSError):
                return
            raise AssertionError('Unexpected acceptance: '+operation)
        source = work / 'source.txt'
        source.write_text('alpha\n日本語\nomega\n')
        assert run('read_file', path='source.txt', start_line=2, max_lines=1)['text'] == '2: 日本語\n'
        passed('F1 numbered text read')
        large = work / 'large'
        with large.open('wb') as f:
            f.seek(32*1024*1024)
            f.write(b'\x00\xff\x01end')
        result = run('read_bytes', path='large', offset=32*1024*1024+1, length=4)
        assert base64.b64decode(result['data']) == b'\xff\x01en'
        passed('F2 byte range in a large file')
        with patch.object(p, 'terminal_confirm', return_value=True) as confirm:
            run('write', path='new.txt', content='hello world')
            assert confirm.call_args.args[0]['after'] == 'hello world'
            assert confirm.call_args.args[0]['before'] == ''
        assert (work/'new.txt').read_text() == 'hello world'
        passed('F3 new file with approved exact diff')
        with patch.object(p, 'terminal_confirm', return_value=True):
            run('edit', path='new.txt', old='world', new='Orbi')
        assert (work/'new.txt').read_text() == 'hello Orbi'
        passed('F4 exact replacement')
        source.write_text('same same')
        with patch.object(p, 'terminal_confirm', side_effect=AssertionError('Must not request approval')):
            rejected('edit', path='source.txt', old='same', new='bad')
        assert source.read_text() == 'same same'
        passed('F5 nonunique edit refused')
        (work/'sub').mkdir()
        (work/'sub/a.py').write_text('def hello():\n    pass\n')
        (work/'sub/a.txt').write_text('def unwanted():\n')
        result = run('glob_files', path='.', pattern='**/*.py')
        assert result['paths'] == [str(work/'sub/a.py')]
        passed('F6 glob pattern')
        result = run('grep_files', path='sub', pattern=r'^def \w+\(', file_type='py')
        assert 'hello' in result['stdout'] and 'unwanted' not in result['stdout'] and result['exit_code'] == 0
        rejected('grep_files', path='missing', pattern='x')
        rejected('grep_files', path='sub', pattern='[')
        passed('F7 regex grep and file-type filter; errors stay errors')
        pdf(work/'test.pdf')
        assert 'ORBI PDF CONTENT' in run('read_pdf', path='test.pdf')['text']
        rejected('read_pdf', path='new.txt')
        # The byte cap can split the final UTF-8 character; retain the captured bytes.
        raw = b'prefix \xe2\x82'
        with patch('file_tools.run_bounded', return_value=dict(exit_code=0, timed_out=False,
                truncated=True, stdout=None, stdout_base64=base64.b64encode(raw).decode(), stderr='')):
            result = run('read_pdf', path='test.pdf')
        assert result['encoding'] == 'base64' and base64.b64decode(result['data']) == raw
        passed('F8 PDF text extraction')
        from test_image_reader import text_image
        text_image(work/'image.png', b'ORBI LOCAL TEXT 12345')
        result = run('read_image', path='image.png')
        assert 'ORBI' in result['text'].upper(), result
        passed('F9 local image decode and OCR (scene understanding unavailable)')
        rejected('write', path=str(kildall.ROOT.parent/'phase41-forbidden'), content='no')
        link = work/'out'
        link.symlink_to(kildall.ROOT.parent/'Researchhub', target_is_directory=True)
        rejected('write', path=str(link/'forbidden'), content='no')
        passed('F10 writes outside root refused')
        result = run('run_command', command='echo hello')
        assert result['stdout'] == 'hello\n' and result['stderr'] == '' and result['exit_code'] == 0
        result = run('run_command', command='ls /this-path-does-not-exist')
        assert result['stderr'] and result['exit_code'] != 0
        passed('S1 real stdout and stderr')
        started = time.monotonic()
        result = run('run_command', command='sleep 3', timeout=1)
        assert result['timed_out'] and result['exit_code'] == -9 and time.monotonic()-started < 2.5
        passed('S2 configurable timeout and actual signal exit')
        child = "import json,sys;from pathlib import Path;import permissions;print(json.dumps(permissions.run_action(Path(sys.argv[1]),sys.argv[2],'run_command',dict(command='sleep 1',timeout=5,background=True))))"
        job = subprocess.run([sys.executable, '-c', child, str(db), str(work)], cwd=kildall.ROOT, capture_output=True, text=True, timeout=10, check=True)
        ident = json.loads(job.stdout)['id']
        for _ in range(80):
            result = run('shell_job', id=ident)
            if result['result'] is not None:
                break
            time.sleep(.05)
        assert result['status'] == 'done' and result['result']['exit_code'] == 0, result
        passed('S3 background command survives its caller; inspectable result')
        result = run('run_command', command='false')
        assert result['exit_code'] == 1
        with kildall.database(db) as connection:
            assert connection.execute('SELECT status FROM orbi_permissions ORDER BY created DESC LIMIT 1').fetchone()[0] == 'failed'
        passed('S4 nonzero exit is logged as failed')
        run('run_command', command='cd sub')
        assert run('run_command', command='pwd')['stdout'].strip() == str(work/'sub')
        assert 'def hello' in run('run_command', command='cat a.py')['stdout']
        passed('S5 cwd persists across calls')
        with patch.object(kildall, 'SYSTEM_RULES', ''):
            for command in ('rm -rf .', 'sudo true', 'git push --force', 'git push origin +HEAD:main',
                            'sh -c true', 'python -c pass', 'osascript -e click', 'screencapture x', 'env true'):
                rejected('run_command', command=command)
        assert run('run_command', command='echo sudo')['stdout'] == 'sudo\n'
        passed('S6 Never actions refused in code with empty system rules; quoted topic remains data')
        # Test the actual kernel boundary with known, non-destructive shell probes.
        sentinel = work/'sandbox-must-not-write'
        for script in (f'echo bad > {sentinel}', '/bin/echo child'):
            result = run_bounded(['/bin/sh', '-c', script], work, 2)
            assert result['exit_code'] != 0 and not sentinel.exists(), result
        with kildall.database(db) as connection:
            assert not connection.execute("SELECT 1 FROM orbi_permissions WHERE status IN ('checking','waiting','running','background')").fetchall()
        assert len(checks) == 16
        print(json.dumps(dict(passed=True, items=checks, extra='Kernel write/child-exec denial verified')))


if __name__ == '__main__':
    main()
