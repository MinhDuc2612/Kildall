"""Closed read-only commands inside the Phase 3 executor; no shell evaluation."""
import base64
import json
import os
from pathlib import Path
import re
import selectors
import shlex
import signal
import subprocess
import sys
import time


def tool(name, description, properties, required):
    return dict(type='function', function=dict(name=name, description=description,
        parameters=dict(type='object', properties=properties, required=required, additionalProperties=False)))


TOOLS = [tool('run_command', 'Run a confined read-only command: echo, printf, true, false, sleep, ls, cat, wc, pwd, cd. No shell syntax. Cwd persists. Writes use write/edit.',
    dict(command=dict(type='string'), timeout=dict(type='integer', minimum=1, maximum=3600), background=dict(type='boolean')), ['command']),
    tool('shell_job', 'Inspect a background command, including stdout, stderr and actual exit code.', dict(id=dict(type='string')), ['id'])]


def run_bounded(argv, cwd, timeout, *, limit=65536, pass_fds=(), started=None):
    """Kernel denies writes, network, GUI IPC and any executable except this binary."""
    argv = [os.path.realpath(argv[0]), *argv[1:]]
    profile = '(version 1)(deny default)(allow file-read*)(allow sysctl-read)(allow process-exec (literal ' + json.dumps(argv[0]) + '))'
    command = ['/usr/bin/sandbox-exec', '-p', profile, *argv]
    proc = subprocess.Popen(command, cwd=cwd, env={'PATH': '/usr/bin:/bin', 'LANG': 'en_US.UTF-8'},
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True, close_fds=True, pass_fds=pass_fds)
    chunks = {'stdout': bytearray(), 'stderr': bytearray()}
    truncated, timed_out = False, False
    deadline = time.monotonic() + timeout
    try:
        if started:
            started(proc.pid)
        with selectors.DefaultSelector() as selector:
            for name in chunks:
                selector.register(getattr(proc, name), selectors.EVENT_READ, name)
            while selector.get_map():
                if not timed_out and time.monotonic() >= deadline and proc.poll() is None:
                    timed_out = True
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                for key, _ in selector.select(0.05):
                    data = os.read(key.fileobj.fileno(), 8192)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    target = chunks[key.data]
                    room = max(0, limit - len(target))
                    truncated |= len(data) > room
                    target.extend(data[:room])
            code = proc.wait()
    finally:
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
        proc.stdout.close()
        proc.stderr.close()
    result = dict(exit_code=code, timed_out=timed_out, truncated=truncated)
    for name, data in chunks.items():
        try:
            result[name] = data.decode('utf-8')
        except UnicodeDecodeError:
            result[name] = None
            result[name + '_base64'] = base64.b64encode(data).decode('ascii')
    return result


def command_args(command, cwd):
    from permissions import COMPUTER_REASON
    if not isinstance(command, str) or len(command) > 16384:
        raise ValueError('Expected a bounded command string')
    parts = shlex.split(command)
    if not parts:
        raise ValueError('Empty command')
    name, args = parts[0], parts[1:]
    # This is an allow-list, never an attempt to sanitize executable shell text.
    binaries = {n: '/bin/' + n for n in ('echo', 'sleep', 'ls', 'cat')}
    binaries.update({n: '/usr/bin/' + n for n in ('printf', 'true', 'false', 'wc')})
    if name in ('cd', 'pwd'):
        if len(args) != (1 if name == 'cd' else 0):
            raise ValueError('cd takes one path; pwd takes no arguments')
        return parts
    if name not in binaries:
        raise PermissionError('Command is outside the closed executable set; ' + COMPUTER_REASON)
    if name in ('true', 'false') and args:
        raise PermissionError('Unexpected command arguments')
    if name == 'sleep' and (len(args) != 1 or not re.fullmatch(r'\d+(?:\.\d+)?', args[0]) or float(args[0]) > 3600):
        raise ValueError('sleep requires 0..3600 seconds')
    if name in ('cat', 'wc', 'ls'):
        allowed = {'cat': {'-n', '-b', '-s', '-v', '-e', '-t'},
                   'wc': {'-c', '-l', '-m', '-w'},
                   'ls': {'-a', '-l', '-h', '-1', '-A', '-d', '-F', '-G'}}[name]
        operands, options = [], True
        for arg in args:
            if options and arg == '--':
                options = False
            elif options and arg.startswith('-'):
                if arg not in allowed:
                    raise PermissionError('Unsupported command option')
                operands.append(arg)
            else:
                path = Path(os.path.expanduser(arg))
                path = path if path.is_absolute() else Path(cwd) / path
                # No devices/FIFOs; missing operands remain real command errors.
                if path.exists() and not (path.is_file() or (name == 'ls' and path.is_dir())):
                    raise PermissionError('Expected a regular file or directory')
                operands.append(str(path.absolute()))
        args = operands
    return [binaries[name], *args]


def tables(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS orbi_shell_cwd(project TEXT PRIMARY KEY, cwd TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS orbi_shell_jobs(id TEXT PRIMARY KEY, project TEXT NOT NULL,
            cwd TEXT NOT NULL, command TEXT NOT NULL, timeout INTEGER NOT NULL, result TEXT,
            child_pid INTEGER, child_start TEXT);''')
    columns = {row[1] for row in db.execute('PRAGMA table_info(orbi_shell_jobs)')}
    for name, kind in (('child_pid', 'INTEGER'), ('child_start', 'TEXT')):
        if name not in columns:
            db.execute(f'ALTER TABLE orbi_shell_jobs ADD COLUMN {name} {kind}')


def stop_owned_child(pid, started):
    from orbi import process_start
    if not pid or not started or process_start(pid) != started:
        return
    try:
        if os.getpgid(pid) == pid:
            os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def finish(db_path, ident, result):
    from orbi import database
    status = 'cancelled' if result.get('cancelled') else 'timed_out' if result['timed_out'] else 'done' if result['exit_code'] == 0 else 'failed'
    with database(db_path) as db:
        if db.execute('UPDATE orbi_shell_jobs SET result=? WHERE id=?', (json.dumps(result), ident)).rowcount != 1:
            raise RuntimeError('Shell job disappeared')
        if db.execute('UPDATE orbi_permissions SET status=?,reason=?,updated=? WHERE id=?',
                      (status, result['stderr'] or None, time.time(), ident)).rowcount != 1:
            raise RuntimeError('Shell permission disappeared')


def execute(operation, args, record, project):
    from orbi import database, process_start
    from permissions import authorize
    db_path, ident = record['db_path'], record['id']
    with database(db_path) as db:
        tables(db)
        if operation == 'shell_job':
            row = db.execute('SELECT j.*, p.status,p.pid,p.owner_start FROM orbi_shell_jobs j JOIN orbi_permissions p ON j.id=p.id WHERE j.id=? AND j.project=?', (args['id'], project)).fetchone()
            if row is None:
                raise PermissionError('No background job belongs to this project')
            authorize(record, 'Auto')
            result = json.loads(row['result']) if row['result'] else None
            if result is None and process_start(row['pid']) != row['owner_start']:
                # Worker may have committed between our first read and the liveness check.
                db.execute("UPDATE orbi_permissions SET status='interrupted',reason='Worker ended without a result',updated=? WHERE id=? AND EXISTS (SELECT 1 FROM orbi_shell_jobs WHERE id=? AND result IS NULL)", (time.time(), row['id'], row['id']))
                row = db.execute('SELECT j.*, p.status FROM orbi_shell_jobs j JOIN orbi_permissions p ON j.id=p.id WHERE j.id=?', (row['id'],)).fetchone()
                result = json.loads(row['result']) if row['result'] else None
                if result is None:
                    stop_owned_child(row['child_pid'], row['child_start'])
            return dict(id=row['id'], status=row['status'], result=result)
        row = db.execute('SELECT cwd FROM orbi_shell_cwd WHERE project=?', (project,)).fetchone()
    cwd = row['cwd'] if row else project
    argv = command_args(args['command'], cwd)
    timeout, background = args.get('timeout', 30), args.get('background', False)
    if argv[0] in ('pwd', 'cd'):
        if background:
            raise ValueError('Directory operations cannot be backgrounded')
        if argv[0] == 'cd':
            path = Path(os.path.expanduser(argv[1]))
            path = (path if path.is_absolute() else Path(cwd) / path).resolve(strict=True)
            fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
            os.close(fd)
            cwd = str(path)
        authorize(record, 'Auto')
        with database(db_path) as db:
            db.execute('INSERT INTO orbi_shell_cwd VALUES(?,?) ON CONFLICT(project) DO UPDATE SET cwd=excluded.cwd', (project, cwd))
        return dict(stdout=cwd+'\n', stderr='', exit_code=0, cwd=cwd, timed_out=False, truncated=False)
    authorize(record, 'Auto')
    if not background:
        result = run_bounded(argv, cwd, timeout)
        record['update'](status='timed_out' if result['timed_out'] else 'done' if result['exit_code'] == 0 else 'failed', reason=result['stderr'] or None)
        return dict(result, cwd=cwd)
    with database(db_path) as db:
        db.execute('INSERT INTO orbi_shell_jobs(id,project,cwd,command,timeout,result) VALUES(?,?,?,?,?,NULL)',
                   (ident, project, cwd, args['command'], timeout))
    proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(Path(db_path).resolve()), ident],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        cwd=Path(__file__).parent, start_new_session=True, close_fds=True)
    try:
        with database(db_path) as db:
            db.execute("UPDATE orbi_permissions SET status='background',pid=?,owner_start=?,updated=? WHERE id=?", (proc.pid, process_start(proc.pid), time.time(), ident))
        record['status'] = 'background'
        proc.stdin.write(b'1')
        proc.stdin.close()
    except BaseException:
        proc.kill()
        proc.wait()
        raise
    return dict(id=ident, status='background', cwd=cwd)


def worker(db_path, ident):
    from orbi import database, process_start

    def terminated(signum, frame):
        raise KeyboardInterrupt('Shell worker terminated')

    def started(pid):
        owner = process_start(pid)
        with database(db_path) as db:
            if db.execute('UPDATE orbi_shell_jobs SET child_pid=?,child_start=? WHERE id=? AND result IS NULL',
                          (pid, owner, ident)).rowcount != 1:
                raise RuntimeError('Shell job disappeared before command startup')

    signal.signal(signal.SIGTERM, terminated)
    if sys.stdin.buffer.read(1) != b'1':
        raise RuntimeError('Missing parent handoff')
    with database(db_path) as db:
        row = db.execute('SELECT * FROM orbi_shell_jobs WHERE id=? AND result IS NULL', (ident,)).fetchone()
    if row is None:
        raise RuntimeError('Missing pending job')
    try:
        result = run_bounded(command_args(row['command'], row['cwd']), row['cwd'], row['timeout'], started=started)
    except BaseException as error:
        result = dict(stdout='', stderr=str(error), exit_code=None, timed_out=False, truncated=False,
                      cancelled=isinstance(error, (KeyboardInterrupt, SystemExit)))
    finish(db_path, ident, result)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Internal background worker')
    worker(*sys.argv[1:])
