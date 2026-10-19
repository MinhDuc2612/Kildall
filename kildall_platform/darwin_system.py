"""Existing Mac host operations; no alternative binaries or weaker fallbacks."""
import fcntl
import json
import os
from pathlib import Path
import plistlib
import re
import subprocess
import time


def executable(name):
    binaries = {n: '/bin/' + n for n in ('echo', 'sleep', 'ls', 'cat', 'bash')}
    binaries.update({n: '/usr/bin/' + n for n in ('printf', 'true', 'false', 'wc')})
    binaries.update({n: '/opt/homebrew/bin/' + n for n in ('git', 'gh', 'rg', 'pdftotext')})
    return binaries[name]


def shell_binaries():
    return {name: executable(name) for name in ('echo', 'sleep', 'ls', 'cat', 'printf', 'true', 'false', 'wc')}


def sandbox_command(argv):
    argv = [os.path.realpath(argv[0]), *argv[1:]]
    profile = '(version 1)(deny default)(allow file-read*)(allow sysctl-read)(allow process-exec (literal ' + json.dumps(argv[0]) + '))'
    return ['/usr/bin/sandbox-exec', '-p', profile, *argv]


def process_start(pid):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'lstart='],
                            text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def process_command(pid):
    return subprocess.run(['ps', '-p', str(pid), '-o', 'command='],
                          text=True, capture_output=True)


def process_command_text(pid):
    return subprocess.check_output(['ps', '-p', str(pid), '-o', 'command='], text=True)


def lock(file, *, exclusive=True, nonblocking=False):
    mode = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
    fcntl.flock(file, mode | (fcntl.LOCK_NB if nonblocking else 0))


def unlock(file):
    fcntl.flock(file, fcntl.LOCK_UN)


def memory_available():
    text = subprocess.check_output(['vm_stat'], text=True, timeout=5)
    page = int(re.search(r'page size of (\d+)', text)[1])
    pages = {k: int(v) for k, v in re.findall(r'^([^:\n]+):\s+(\d+)\.', text, re.M)}
    available = page * sum(pages[k] for k in ('Pages free', 'Pages inactive', 'Pages speculative'))
    pressure = int(subprocess.check_output(['sysctl', '-n', 'kern.memorystatus_vm_pressure_level'], text=True, timeout=5))
    return available, pressure


def command(*args):
    return subprocess.check_output(args, text=True, timeout=10).strip()


def sample_memory(pid, started):
    devices = plistlib.loads(command('ioreg', '-r', '-c', 'AGXAccelerator', '-a').encode())
    gpu = next(d['PerformanceStatistics'] for d in devices if 'PerformanceStatistics' in d)
    return dict(
        elapsed_s=time.monotonic() - started,
        rss_bytes=int(command('ps', '-p', str(pid), '-o', 'rss=')) * 1024,
        pressure=int(command('sysctl', '-n', 'kern.memorystatus_vm_pressure_level')),
        free_percent=int(re.search(r'free percentage: (\d+)%', command('memory_pressure', '-Q'))[1]),
        swap=command('sysctl', '-n', 'vm.swapusage'),
        gpu_in_use_bytes=int(gpu['In use system memory']),
        gpu_allocated_bytes=int(gpu['Alloc system memory']),
    )


def wired_limit_text(*, absolute=True, timed=False):
    binary = '/usr/sbin/sysctl' if absolute else 'sysctl'
    if timed:
        return command(binary, '-n', 'iogpu.wired_limit_mb')
    return subprocess.check_output([binary, '-n', 'iogpu.wired_limit_mb'], text=True).strip()


def wired_limit():
    return int(wired_limit_text())


def self_peak_rss_bytes():
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def check_gpu():
    import mlx.core as mx
    device = mx.default_device()
    if device != mx.gpu:
        raise SystemExit(f'ERROR: MLX must use a GPU; got {device}')
    return device


def data_volume():
    return '/System/Volumes/Data'


def backup_volume():
    return Path('/Volumes/KildallC')


def guard_path(candidate, root):
    """Keep realpath/component containment; never lowercase an APFS path."""
    root = Path(root).absolute()
    if os.path.realpath(root) != str(root):
        raise PermissionError('Allowed root must not redirect through a symlink')
    resolved = Path(os.path.realpath(os.path.expanduser(os.fspath(candidate))))
    if not resolved.is_relative_to(root):
        raise PermissionError('Path resolves outside the allowed root')
    return resolved


def runtime_artifact():
    return ('.tools/llama-b10809.tar.gz', 11123196,
            '7d692df9e1e386e62f1c12b843903218041e6cd74c9415aa39a7ed3176f9eaa2',
            'https://github.com/ggml-org/llama.cpp/releases/download/b10809/llama-b10809-bin-macos-arm64.tar.gz')
