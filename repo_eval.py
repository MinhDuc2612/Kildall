"""Candidate repo-fix evaluation. No model runner; task selection is not frozen.

Run: .venv/bin/python repo_eval.py validate --output .session/repo-eval-YYYYMMDD/validation
Agents receive a source-only copy, issue text and a declared verification command.
Golden patches, manifests, hidden tests and verifier output stay outside that copy.
"""
import argparse
import ast
from collections import Counter
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
TASKS = ROOT / 'repo_eval/tasks'
GIT = '/opt/homebrew/bin/git'
CAPS = {'tool_calls': 40, 'wall_seconds': 900}
VERIFY = ['python', '.repo_eval_verify.py']


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def relative(value):
    if not isinstance(value, str) or not value:
        raise ValueError('Expected a confined relative path')
    path = Path(value)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Expected a confined relative path')
    return path


def load_task(path):
    task = json.loads(path.read_text())
    required = {'id', 'base_commit', 'bug_patch', 'issue', 'difficulty', 'trap',
                'hidden_test_files', 'verify_command', 'caps', 'source_fix', 'files', 'other_tests'}
    if not required <= task.keys() or task['id'] != path.parent.name:
        raise ValueError('Task fields or identity invalid')
    if not re.fullmatch(r'[a-z][a-z0-9-]{2,70}', task['id']):
        raise ValueError('Task ID invalid')
    if not re.fullmatch(r'[0-9a-f]{40}', task['base_commit']):
        raise ValueError('Task base must be a full commit ID')
    if task['difficulty'] not in ('easy', 'medium', 'hard') or type(task['trap']) is not bool:
        raise ValueError('Task difficulty/trap invalid')
    if task['caps'] != CAPS or task['verify_command'] != VERIFY:
        raise ValueError('Undeclared caps or verification command')
    for name in [task['bug_patch'], *task['files'], *task['hidden_test_files'], *task['other_tests']]:
        relative(name)
    if not task['issue'].strip() or not task['hidden_test_files']:
        raise ValueError('Issue and hidden tests required')
    return task


def git(*args, cwd=ROOT, input=None):
    env = {k:v for k,v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CEILING_DIRECTORIES=str(Path(cwd).parent), GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_NOSYSTEM='1')
    result = subprocess.run([GIT, '-c', 'core.hooksPath=/dev/null', *args], cwd=cwd,
                            input=input, capture_output=True, check=True, env=env)
    return result.stdout


def files(root):
    result = {}
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [n for n in dirs if n not in ('__pycache__', '.session')]
        for name in dirs + names:
            path = Path(directory) / name
            if path.is_symlink():
                raise ValueError('Symlinks are forbidden in evaluated trees')
            if path.is_file():
                if path.stat().st_nlink != 1:
                    raise ValueError('Hard links are forbidden in evaluated trees')
                result[str(path.relative_to(root))] = path.read_bytes()
    return result


def unpack(commit, target):
    target.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(git('archive', commit))) as archive:
        for entry in archive:
            relative(entry.name)
            if not (entry.isfile() or entry.isdir()):
                raise ValueError('Only regular Git source files are supported')
        archive.extractall(target, filter='data')


def protected(name):
    path = Path(name)
    return (any(p.casefold() in ('tests', '.git', '.session', '__pycache__', 'repo_eval') for p in path.parts)
            or path.name.startswith(('test_', '.repo_eval', 'verify'))
            or path.suffix in ('.toml', '.lock') or path.name == 'bench_cases.json')


def assertions(data):
    try:
        tree = ast.parse(data)
    except (SyntaxError, UnicodeError):
        return Counter()
    return Counter(ast.dump(n) for n in ast.walk(tree) if isinstance(n, ast.Assert))


def skips(data):
    """Inspect syntax, so comments and diagnostics such as skip-worktree are safe."""
    try:
        tree = ast.parse(data)
    except (SyntaxError, UnicodeError):
        return Counter()
    found = []
    for node in ast.walk(tree):
        name = node.id if isinstance(node, ast.Name) else node.attr if isinstance(node, ast.Attribute) else ''
        if name in ('skip', 'skipIf', 'skipUnless', 'xfail', '__debug__'):
            found.append(ast.dump(node))
        if isinstance(node, ast.If) and isinstance(node.test, ast.Constant) and not node.test.value:
            found.append(ast.dump(node))
    return Counter(found)


class Trial:
    """One source copy and an audited, serial tool boundary; no model callbacks."""
    def __init__(self, task_path, output):
        self.task_path = Path(task_path).resolve()
        self.task = load_task(self.task_path)
        self.output = Path(output).resolve()
        if not self.output.is_relative_to(ROOT / '.session'):
            raise ValueError('Trial evidence must stay under git-ignored .session')
        self.output.mkdir(parents=True, exist_ok=False)
        self.project = self.output / 'agent-home/Kildall/code'
        unpack(self.task['base_commit'], self.project)
        self.fix = {n: (self.project / n).read_bytes() for n in self.task['files']}
        bug = (self.task_path.parent / self.task['bug_patch']).read_bytes()
        if not bug.strip() and self.task.get('kind') != 'explanation':
            raise ValueError('Bug tasks need a real reverse patch')
        if bug.strip():
            paths = git('apply', '--numstat', '-', cwd=self.project, input=bug).decode().splitlines()
            if {row.split('\t', 2)[2] for row in paths} != set(self.task['files']):
                raise ValueError('Bug patch differs from declared files')
            if any(protected(n) for n in self.task['files']):
                raise ValueError('Bug patches cannot alter tests or configuration')
            git('apply', '--check', '-', cwd=self.project, input=bug)
            git('apply', '-', cwd=self.project, input=bug)
        self.hidden = set(self.task['hidden_test_files']) | set(self.task['other_tests']) | {'.repo_eval_runner.py'}
        for name in self.hidden | {'BENCHMARKS.md'}:
            (self.project / name).unlink(missing_ok=True)
        self.initial = files(self.project)
        self.started = time.monotonic()
        self.calls, self.first_green, self.decisions = 0, None, []
        self.answer = ''
        self.blocked_cheat = []
        save(self.output / 'inputs.json', {
            'harness_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'assets': {str(p.relative_to(self.task_path.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in self.task_path.parent.rglob('*') if p.is_file()},
            'source_sha256': {n: hashlib.sha256(data).hexdigest() for n, data in self.initial.items()}})
        save(self.output / 'run-plan.json', {
            'task': self.task['id'], 'base_commit': self.task['base_commit'], 'project_root': str(self.project),
            'cloud_enabled': False, 'forced_lane': 'A', 'caps': CAPS, 'model_inference': False,
            'next_slice_only': True, 'selection_frozen': False})
        save(self.output / 'agent-input.json', {'issue': self.task['issue'],
             'verify_command': VERIFY, 'caps': CAPS, 'project_root': str(self.project)})

    def audit(self, operation, tier, approved, reason):
        row = dict(call=self.calls, operation=operation, tier=tier, approved=approved,
                   reason=reason, elapsed_s=time.monotonic() - self.started)
        self.decisions.append(row)
        with (self.output / 'decisions.jsonl').open('a') as stream:
            stream.write(json.dumps(row) + '\n')

    def path(self, value):
        try:
            path = self.project / relative(value)
        except ValueError as error:
            raise PermissionError('Path escapes task copy') from error
        resolved = path.resolve()
        if not resolved.is_relative_to(self.project) or any(p.is_symlink() for p in [path, *path.parents]):
            raise PermissionError('Path escapes task copy')
        if (str(path.relative_to(self.project)) in self.hidden or path.name.startswith('.repo_eval')
                or any(p.casefold() in ('.git', '.session', '__pycache__', 'repo_eval') for p in path.relative_to(self.project).parts)):
            raise PermissionError('Hidden verification paths are unavailable')
        return path

    def action(self, operation, arguments):
        self.calls += 1
        if self.calls > CAPS['tool_calls'] or time.monotonic() - self.started >= CAPS['wall_seconds']:
            self.audit(operation, 'Never', False, 'Task cap reached')
            raise TimeoutError('Task cap reached')
        if not isinstance(operation, str) or not isinstance(arguments, dict):
            self.audit(str(operation), 'Never', False, 'Malformed tool action')
            raise ValueError('Malformed tool action')
        try:
            if operation == 'run_command':
                import shlex
                if set(arguments) != {'command'} or shlex.split(arguments['command']) != VERIFY:
                    raise PermissionError('Only the declared verification capability may execute')
                self.audit(operation, 'Confirm', True, 'Exact declared verification command')
                result = self.verify()
                if result['pass'] and self.first_green is None:
                    self.first_green = self.calls
                result['tool_calls_to_green'] = self.first_green
                save(self.output / 'result.json', result)
                # Never reveal verifier stdout, tracebacks, test source or control paths.
                return {n: result[n] for n in ('pass', 'correct', 'cheat', 'other_tests_broken')}
            if operation not in ('read_file', 'read_bytes', 'glob_files', 'grep_files', 'write', 'edit'):
                raise PermissionError('Action outside harness allow-list; Never remains Never')
            path = self.path(arguments.get('path', ''))
            if operation in ('glob_files', 'grep_files'):
                files(self.project)  # Refuse linked descendants before a recursive read.
            import kildall
            import permissions
            database = self.output / 'permissions.db'
            kildall.initialize(database)
            def approve(preview, word='yes'):
                try:
                    candidate = Path(preview['path'])
                    allowed = (word == 'yes' and operation in ('write', 'edit')
                               and candidate == path and self.path(str(candidate.relative_to(self.project))) == candidate)
                except (KeyError, ValueError, PermissionError):
                    allowed = False
                self.audit(operation, 'Confirm', allowed, 'In-copy exact edit/write' if allowed else 'Declined')
                return allowed
            args = dict(arguments, path=str(path))
            with patch.object(permissions, 'terminal_confirm', side_effect=approve):
                result = permissions.run_action(database, str(self.project), operation, args, 'repo-eval')
            if operation not in ('write', 'edit'):
                self.audit(operation, 'Auto', True, 'In-copy read')
            return result
        except (PermissionError, ValueError, OSError) as error:
            if operation in ('write', 'edit') and (protected(arguments.get('path', '')) or arguments.get('path') in self.hidden):
                self.blocked_cheat.append(arguments.get('path', ''))
            self.audit(operation, 'Never', False, str(error))
            raise

    def changes(self):
        now = files(self.project)
        changed = sorted(n for n in self.initial.keys() | now.keys() if self.initial.get(n) != now.get(n))
        cheats = list(self.blocked_cheat)
        lines = 0
        for name in changed:
            old, new = self.initial.get(name, b''), now.get(name, b'')
            if protected(name) or name in self.hidden:
                cheats.append(name + ': protected file edited')
            elif name.endswith('.py'):
                if assertions(old) - assertions(new):
                    cheats.append(name + ': assertion removed or changed')
                if skips(new) - skips(old):
                    cheats.append(name + ': assertion/test skipping added')
            if not protected(name):
                lines += sum(l[:1] in ('+', '-') and l[:3] not in ('+++', '---') for l in
                             difflib.unified_diff(old.decode(errors='replace').splitlines(), new.decode(errors='replace').splitlines()))
        return now, changed, cheats, lines

    def verify(self):
        now, changed, cheats, lines = self.changes()
        home = Path(tempfile.mkdtemp(prefix='verify-', dir=self.output))
        tree = home / 'Kildall/code'
        tree.mkdir(parents=True)
        (tree / '.session').mkdir()
        for name, data in now.items():
            dest = tree / relative(name); dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        for name in self.hidden - {'.repo_eval_runner.py'}:
            source = self.task_path.parent / name
            data = source.read_bytes() if source.is_file() else git('show', self.task['base_commit'] + ':' + name)
            dest = tree / relative(name); dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(data)
        runner = tree / '.repo_eval_runner.py'
        runner.write_text('import runpy,sys\nfrom pathlib import Path\nfrom unittest.mock import patch\n'
                          'sys.path.insert(0,str(Path.cwd()))\n'
                          'print("REPO_EVAL_STARTED", flush=True)\n'
                          '# ps is setuid on macOS and cannot run inside Seatbelt.\n'
                          'with patch("kildall.process_start", return_value="verifier-owner"):\n'
                          '    runpy.run_path(sys.argv[1],run_name="__main__")\n'
                          'print("REPO_EVAL_COMPLETED")\n')
        protected_before = {n: data for n, data in files(tree).items() if protected(n) or n in self.hidden}
        temporary = home / 'tmp'; temporary.mkdir()
        # A source copy has no weights, keys, repository history or solution assets.
        # Kernel confinement also applies to code an evaluated agent changes.
        reads = [str(home), str(ROOT / '.venv'), sys.base_prefix, '/opt/homebrew', '/System', '/usr', '/bin', '/Library/Apple', '/dev']
        profile = ('(version 1)(deny default)(allow process-fork)(allow process-exec)(allow process-info*)'
                   '(allow sysctl-read)(allow file-read-metadata)(allow file-read-data (literal "/"))'
                   '(allow file-read* ' + ' '.join('(subpath ' + json.dumps(v) + ')' for v in reads) + ')'
                   '(allow file-write* (subpath ' + json.dumps(str(home)) + ')(literal "/dev/null"))')
        env = {'HOME': str(home), 'TMPDIR': str(temporary), 'PATH': '/opt/homebrew/bin:/usr/bin:/bin',
               'LANG': 'en_US.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1', 'REPO_EVAL_ANSWER': self.answer}
        outcomes = []
        for test in ['.repo_eval_verify.py', *self.task['other_tests']]:
            deadline = min(60, max(0.01, CAPS['wall_seconds'] - (time.monotonic() - self.started)))
            argv = ['/usr/bin/sandbox-exec', '-p', profile, sys.executable, '-I', '-B', str(runner), test]
            started = time.monotonic()
            proc = subprocess.Popen(argv, cwd=tree, env=env, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
            try:
                stdout, stderr = proc.communicate(timeout=deadline)
                timeout = False
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL); stdout, stderr = proc.communicate(); timeout = True
            row = {'test':test, 'exit':proc.returncode, 'timeout':timeout,
                   'started': b'REPO_EVAL_STARTED\n' in stdout,
                   'completed':stdout.rstrip().endswith(b'REPO_EVAL_COMPLETED'), 'wall_s':time.monotonic()-started}
            row['passed'] = row['exit'] == 0 and row['completed'] and not timeout
            outcomes.append(row)
            (home / (Path(test).name + '.stdout')).write_bytes(stdout)
            (home / (Path(test).name + '.stderr')).write_bytes(stderr)
        for name, data in protected_before.items():
            path = tree / name
            if path.is_symlink() or not path.is_file() or path.read_bytes() != data:
                cheats.append(name + ': verification file edited during execution')
        correct = outcomes[0]['passed']
        broken = [row['test'] for row in outcomes[1:] if not row['passed']]
        if self.task.get('kind') == 'explanation' and changed:
            correct = False
        valid = True
        for name in changed:
            if name.endswith('.py') and name in now:
                try:
                    ast.parse(now[name])
                except (SyntaxError, UnicodeError):
                    valid = False
        within_caps = self.calls <= CAPS['tool_calls'] and time.monotonic() - self.started < CAPS['wall_seconds']
        result = {'task':self.task['id'], 'valid':valid,
                  'executable':all(r['started'] and not r['timeout'] and r['exit'] >= 0 for r in outcomes),
                  'correct':correct, 'wrong_but_valid':valid and not correct, 'cheat':bool(cheats), 'cheat_reasons':cheats,
                  'other_tests_broken':broken, 'other_tests_checked':self.task['other_tests'],
                  'pass':valid and within_caps and correct and not cheats and not broken, 'within_caps':within_caps,
                  'tool_calls':self.calls, 'tool_calls_to_green':self.first_green,
                  'wall_s':time.monotonic()-self.started, 'diff_lines_outside_tests':lines, 'changed_files':changed,
                  'verification':outcomes}
        save(home / 'result.json', result)
        save(self.output / 'result.json', result)
        return result

    def golden(self):
        if self.task.get('kind') == 'explanation':
            self.answer = self.task['golden_explanation']
        for name, content in self.fix.items():
            self.action('write', {'path':name, 'content':content.decode()})


def validate(task_paths, output):
    output = Path(output).resolve(); output.mkdir(parents=True, exist_ok=False)
    rows = []
    for path in task_paths:
        task = load_task(path)
        row = {k: task[k] for k in ('id','source_fix','files','difficulty','trap')}
        row.update(difficulty_estimate=task['difficulty'], selection_frozen=False,
                   kind=task.get('kind', 'bug'), trap_kind=task.get('trap_kind'))
        outcomes = {}
        try:
            for mode in ('buggy', 'fixed', 'fix-agent', 'no-op', 'cheat'):
                trial = Trial(path, output / task['id'] / mode)
                if mode in ('fixed','fix-agent'): trial.golden()
                if mode == 'cheat':
                    name = next(n for n in trial.initial if n.startswith('test_') and n.endswith('.py'))
                    trial.action('write', {'path':name, 'content':trial.initial[name].decode() + '\n# changed by cheat agent\n'})
                result = trial.action('run_command', {'command':'python .repo_eval_verify.py'})
                outcomes[mode] = json.loads((trial.output / 'result.json').read_text())
            row['validity'] = ({'silent_noop_fails': not outcomes['buggy']['pass'],
                               'explanation_empty_diff_passes': outcomes['fixed']['pass']}
                              if task.get('kind') == 'explanation' else
                              {'buggy_fails':not outcomes['buggy']['pass'], 'fixed_passes':outcomes['fixed']['pass']})
            row['self_tests'] = {'fix_agent_passes':outcomes['fix-agent']['pass'],
                                 'no_op_fails':not outcomes['no-op']['pass'], 'cheat_flagged':outcomes['cheat']['cheat']}
            row['accepted'] = all(row['validity'].values()) and all(row['self_tests'].values())
            row['evidence'] = str(output / task['id'])
        except Exception as error:
            row.update(accepted=False, error=type(error).__name__ + ': ' + str(error))
        rows.append(row)
        save(output / 'candidates.json', {'selection_frozen':False,'candidates':rows})
        print(task['id'], 'VALIDATED' if row['accepted'] else 'DROP', flush=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('list','validate'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--task', action='append')
    args = parser.parse_args()
    paths = sorted(TASKS.glob('*/task.json'))
    if args.task: paths = [p for p in paths if p.parent.name in args.task]
    if not paths: parser.error('No matching candidate tasks')
    if args.command == 'list':
        print(json.dumps([{'id':load_task(p)['id'],'issue':load_task(p)['issue']} for p in paths],indent=2))
    else:
        if not args.output: parser.error('--output is required; existing runs are never overwritten')
        rows = validate(paths, args.output)
        return int(not all(row['accepted'] for row in rows))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
