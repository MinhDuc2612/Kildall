"""Exact captures and worker lifecycle controls; no models or unrestricted shell."""

import base64
import itertools
import json
import os
from pathlib import Path
import shlex
import signal
import tempfile
import time
from unittest.mock import patch

import orbi
import permissions
import shell_tools as shell


def until(predicate, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.02)
    raise AssertionError("Timed out waiting for worker state")


def main():
    with tempfile.TemporaryDirectory(prefix='orbi-shell-lifecycle-') as directory:
        root = Path(directory).resolve()
        db_path, project = root / 'audit.sqlite3', str(root)
        orbi.initialize(db_path)

        def run(name, **args):
            return permissions.run_action(db_path, project, name, args)

        def job_row(ident):
            with orbi.database(db_path) as db:
                return dict(db.execute('SELECT j.*,p.pid,p.owner_start,p.status FROM orbi_shell_jobs j '
                                       'JOIN orbi_permissions p ON p.id=j.id WHERE j.id=?', (ident,)).fetchone())

        binary = root / 'binary'
        binary.write_bytes(b'hello\xff\x00world')
        result = run('run_command', command='cat ' + shlex.quote(str(binary)))
        assert result['exit_code'] == 0 and result['stdout'] is None and not result['truncated']
        assert base64.b64decode(result['stdout_base64']) == binary.read_bytes()
        assert result['stderr'] == ''
        print('PASS: invalid UTF-8 stdout is preserved exactly as base64')

        # Buffered output can remain after a process has exited, past its deadline.
        class FinishedProcess:
            pid = 99999999

            def __init__(self):
                for name, content in (('stdout', b'\xffOUT'), ('stderr', b'\xfeERR')):
                    read, write = os.pipe()
                    os.write(write, content)
                    os.close(write)
                    setattr(self, name, os.fdopen(read, 'rb'))

            def poll(self):
                return 0

            def wait(self):
                return 0

        clock = itertools.chain([0], itertools.repeat(2))
        with patch.object(shell.subprocess, 'Popen', return_value=FinishedProcess()), \
             patch.object(shell.time, 'monotonic', side_effect=lambda: next(clock)), \
             patch.object(shell.os, 'killpg', side_effect=AssertionError('Exited process was killed')):
            result = shell.run_bounded(['/usr/bin/true'], project, 1, limit=3)
        assert result['exit_code'] == 0 and not result['timed_out'] and result['truncated']
        assert base64.b64decode(result['stdout_base64']) == b'\xffOU'
        assert base64.b64decode(result['stderr_base64']) == b'\xfeER'
        print('PASS: bounded binary streams survive; draining an exited process never marks timeout')

        result = run('run_command', command='sleep 5', timeout=1)
        assert result['timed_out'] and result['exit_code'] == -signal.SIGKILL
        with orbi.database(db_path) as db:
            assert db.execute('SELECT status FROM orbi_permissions ORDER BY created DESC LIMIT 1').fetchone()[0] == 'timed_out'
        print('PASS: a live command is killed at its timeout and its actual exit is logged')

        # Commit completion specifically between the polling SELECT and liveness check.
        with permissions.decision(db_path, project, 'run_command', {'command': 'echo complete'}) as record:
            permissions.authorize(record, 'Auto')
            record['update'](status='background')
            ident = record['id']
            with orbi.database(db_path) as db:
                shell.tables(db)
                db.execute('INSERT INTO orbi_shell_jobs(id,project,cwd,command,timeout,result) VALUES(?,?,?,?,?,NULL)',
                           (ident, project, project, 'echo complete', 1))
                db.execute('UPDATE orbi_permissions SET pid=?,owner_start=? WHERE id=?',
                           (99999998, 'old-owner', ident))
        completed = dict(stdout='complete\n', stderr='', exit_code=0, timed_out=False, truncated=False)
        process_start = orbi.process_start

        def finish_during_poll(pid):
            if pid == 99999998:
                shell.finish(db_path, ident, completed)
                return None
            return process_start(pid)

        with patch.object(orbi, 'process_start', side_effect=finish_during_poll):
            polled = run('shell_job', id=ident)
        assert polled['status'] == 'done' and polled['result'] == completed
        assert job_row(ident)['status'] == 'done'
        print('PASS: completion racing with polling retains the finished result and status')

        with patch.object(shell.os, 'killpg', side_effect=AssertionError('Mismatched process was killed')):
            shell.stop_owned_child(os.getpid(), 'wrong-process-start')
        print('PASS: cleanup refuses to signal a reused or unrelated process identity')

        owned = []
        try:
            for termination, expected in ((signal.SIGKILL, 'interrupted'), (signal.SIGTERM, 'cancelled')):
                launched = run('run_command', command='sleep 30', timeout=10, background=True)
                ident = launched['id']
                initial = job_row(ident)
                owned.append((initial['pid'], initial['owner_start']))
                row = until(lambda: (value if (value := job_row(ident))['child_start'] else None))
                child = (row['child_pid'], row['child_start'])
                owned.append(child)
                assert process_start(child[0]) == child[1]
                os.kill(row['pid'], termination)
                until(lambda: process_start(row['pid']) != row['owner_start'])
                polled = run('shell_job', id=ident)
                assert polled['status'] == expected, polled
                until(lambda: process_start(child[0]) != child[1])
                if termination == signal.SIGTERM:
                    assert polled['result']['cancelled'] and 'terminated' in polled['result']['stderr']
                else:
                    assert polled['result'] is None
            print('PASS: polling reaps a hard-killed worker\'s owned command; SIGTERM cleans up and records cancellation')
        finally:
            for pid, started in reversed(owned):
                shell.stop_owned_child(pid, started)
    print('PASS: shell lifecycle controls completed without models or writes outside temporary fixtures')


if __name__ == '__main__':
    main()
