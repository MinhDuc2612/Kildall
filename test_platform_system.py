"""Golden host results against 29ab89b, plus unsupported-platform refusals."""
import ast
from contextlib import redirect_stderr
import io
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

import benchmark
import image_reader
import kildall
import kildall_platform as host
import permissions
import shell_tools
import subagents


ROOT = Path(__file__).resolve().parent


def previous(file, *names):
    source = subprocess.check_output(
        [host.system().executable('git'), 'show', '29ab89b:' + file], cwd=ROOT, text=True)
    tree = ast.parse(source)
    if names:
        tree.body = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.Import, ast.ImportFrom))
                     and (not isinstance(node, ast.FunctionDef) or node.name in names)]
    module = types.ModuleType('golden_' + file.removesuffix('.py'))
    module.__file__ = str(ROOT / file)
    module.CODE_ROOT = permissions.CODE_ROOT
    exec(compile(tree, module.__file__, 'exec'), module.__dict__)
    return module


def outcome(function, *args):
    try:
        return ('ok', function(*args))
    except Exception as error:
        return (type(error).__name__, str(error))


def main():
    native = host.system()
    old_shell = previous('shell_tools.py', 'run_bounded', 'command_args')
    old_process = previous('kildall.py', 'process_start', 'owns_server')
    old_probe = previous('benchmark.py', 'command', 'sample_memory')
    old_capacity = previous('subagents.py', 'capacity')
    for name in ('RESERVE', 'PROCESS_RSS', 'SEPARATE_CERTIFIED'):
        setattr(old_capacity, name, getattr(subagents, name))
    old_guard = previous('permissions.py', 'guard_path')
    old_image = previous('image_reader.py')

    # Compare command argv AND Popen options before any OS execution.
    for argv in (['/bin/echo', 'hi'], ['/bin/bash', '-c', 'printf test'],
                 [native.executable('rg'), '--json', 'a', '.']):
        calls = []
        for function in (old_shell.run_bounded, shell_tools.run_bounded):
            with patch('subprocess.Popen', side_effect=RuntimeError('golden-stop')) as spawn:
                assert outcome(function, argv, ROOT, 2) == ('RuntimeError', 'golden-stop')
                calls.append(spawn.call_args)
        assert calls[0] == calls[1]
    for command in ('echo hello', 'printf %s x', 'ls -G .', 'cat missing', 'wc -l missing',
                    'pwd', 'cd ..', 'sudo true', 'screencapture x', 'osascript x', 'rm -rf x'):
        assert outcome(old_shell.command_args, command, str(ROOT)) == outcome(shell_tools.command_args, command, str(ROOT))

    for code in (0, 1):
        response = subprocess.CompletedProcess([], code, 'Wed Oct 14 20:00:00 2026\n', '')
        calls = []
        for function in (old_process.process_start, kildall.process_start):
            with patch('subprocess.run', return_value=response) as run:
                value = function(1234)
                calls.append((value, run.call_args))
        assert calls[0] == calls[1]
    record = dict(pid=1234, started='start', model='/model.gguf', port=8123)
    for text in ('llama-server -m /model.gguf --port 8123', 'llama-server --port 8124', 'other'):
        response = subprocess.CompletedProcess([], 0, text, '')
        with patch.object(old_process, 'process_start', return_value='start'), \
             patch.object(kildall, 'process_start', return_value='start'), \
             patch('subprocess.run', return_value=response):
            assert old_process.owns_server(record) == kildall.owns_server(record)

    for pressure in (1, 2, 4):
        vm = 'Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free: 100.\nPages inactive: 200.\nPages speculative: 300.\n'
        calls = []
        for function in (old_capacity.capacity, subagents.capacity):
            with patch('subprocess.check_output', side_effect=[vm, str(pressure)]) as run:
                calls.append((function(), run.call_args_list))
        assert calls[0] == calls[1]
        gpu = plistlib.dumps([{'PerformanceStatistics': {'In use system memory': 123, 'Alloc system memory': 456}}]).decode()
        calls = []
        for function in (old_probe.sample_memory, benchmark.sample_memory):
            with patch('subprocess.check_output', side_effect=[gpu, '100', str(pressure), 'free percentage: 42%', 'swap=0']) as run, \
                 patch('time.monotonic', return_value=123):
                calls.append((function(1234, 100), run.call_args_list))
        assert calls[0] == calls[1]

    for absolute, timed in ((True, False), (False, False), (False, True)):
        with patch('subprocess.check_output', return_value='20480\n') as run:
            assert native.wired_limit_text(absolute=absolute, timed=timed) == '20480'
        binary = '/usr/sbin/sysctl' if absolute else 'sysctl'
        expected = (binary, '-n', 'iogpu.wired_limit_mb') if timed else [binary, '-n', 'iogpu.wired_limit_mb']
        assert run.call_args.args == (expected,)
        assert run.call_args.kwargs == dict(text=True, **({'timeout': 10} if timed else {}))
    with patch('resource.getrusage', return_value=types.SimpleNamespace(ru_maxrss=123456)) as usage:
        import resource
        assert native.self_peak_rss_bytes() == 123456
        usage.assert_called_once_with(resource.RUSAGE_SELF)


    with patch('fcntl.flock') as flock:
        import fcntl
        native.lock(7)
        native.lock(8, exclusive=False, nonblocking=True)
        native.unlock(7)
        assert [call.args for call in flock.call_args_list] == [(7, fcntl.LOCK_EX), (8, fcntl.LOCK_SH | fcntl.LOCK_NB), (7, fcntl.LOCK_UN)]
    with tempfile.TemporaryDirectory(dir=ROOT / '.session', prefix='platform-golden-') as directory:
        root = Path(directory)
        (root / 'out').symlink_to(root.parent)
        for path in (root, str(root) + '/', root / '../escape', root / 'out/escape',
                     str(root).replace('Kildall', 'kildall'), '~/Kildall/code'):
            assert outcome(old_guard.guard_path, path, root) == outcome(native.guard_path, path, root)
        from test_image_reader import text_image
        image = root / 'text.png'
        text_image(image, b'ORBI LOCAL TEXT 12345')
        assert old_image.read_image(image) == image_reader.read_image(image)
        (root / 'bad.png').write_bytes(b'not an image')
        assert outcome(old_image.read_image, root / 'bad.png') == outcome(image_reader.read_image, root / 'bad.png')

    # No import or capability can quietly choose a Unix shell/key fallback.
    import cloud_keys
    import backup_ops
    import install_wiredlimit
    import benchmark_mlx
    import prepare_dwq
    for platform in ('linux', 'win32'):
        with patch.object(sys, 'platform', platform), patch('subprocess.Popen') as spawn, \
             patch('subprocess.run') as run, patch.object(cloud_keys, 'parse_env') as read:
            actions = [host.system, host.keys, host.jobs, host.ocr,
                       lambda: shell_tools.run_bounded(['/bin/echo', 'unsafe'], ROOT, 1),
                       lambda: shell_tools.command_args('pwd', str(ROOT)),
                       lambda: shell_tools.execute('run_command', {'command': 'cd ..'}, {}, str(ROOT)),
                       lambda: permissions.execute('shell', {'command': 'ls'}, {}, str(ROOT)),
                       lambda: permissions.execute('run_command', {'command': 'pwd'}, {}, str(ROOT)),
                       lambda: cloud_keys.import_keys('/must-not-read'),
                       lambda: cloud_keys.check_keys([]), lambda: cloud_keys.get_key('GEMINI_API_KEY'),
                       lambda: image_reader.read_image('/must-not-read'), lambda: kildall.process_start(1),
                       lambda: subagents.capacity(), lambda: backup_ops.schedule_backups({}, ROOT, sys.executable),
                       install_wiredlimit.main, lambda: host.refuse_computer(''),
                       benchmark_mlx.main, benchmark_mlx.self_check,
                       lambda: benchmark_mlx.MLXChat('/must-not-load'), prepare_dwq.main,
                       lambda: prepare_dwq.train('/must-not-load')]
            for action in actions:
                try:
                    action()
                except host.UnsupportedPlatform as error:
                    assert 'not implemented' in str(error) and platform in str(error)
                else:
                    raise AssertionError('Unsupported platform silently proceeded')
            for argv in (['keys', 'import', '/must-not-read'], ['keys', 'check'],
                         ['cloud', 'enable', 'llm7']):
                output = io.StringIO()
                with redirect_stderr(output), patch.object(kildall, 'settings') as settings:
                    assert kildall.cloud_main(argv) == 1
                assert 'not implemented' in output.getvalue() and platform in output.getvalue()
                settings.assert_not_called()
            spawn.assert_not_called()
            run.assert_not_called()
            read.assert_not_called()
    print('PASS: Darwin sandbox/paths/process/locks/probes/OCR golden parity; Linux/Windows fail closed before shell/key operations.')


if __name__ == '__main__':
    main()
