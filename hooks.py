"""Explicit, snapshotted shell hooks. Outputs are data; hooks never grant permission."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import tomllib

# This shell policy is an additional veto, not a substitute for permissions.execute.
# $1 phase, $2 operation, $3 JSON event, $4 canonical scope, $5 command, $6 branch.
NEVER = '''case "$2" in
read|ls|git_status|remember|recall|web_data|read_file|read_bytes|glob_files|grep_files|read_pdf|read_image|shell_job|skills|load_skill) ;;
write|edit|install|commit|git_read|git_branch|git_switch|git_commit|git_push|git_pr)
    test "$4" = inside || { printf '%s\\n' 'Never: mutation/repository outside allowed root'; exit 77; } ;;
run_command|shell)
    case "$5" in echo|printf|true|false|sleep|ls|cat|wc|pwd|cd|git-status) ;;
        *) printf '%s\\n' 'Never: command outside closed set (including computer use)'; exit 77 ;; esac ;;
*) printf '%s\\n' 'Never: action outside closed set (including computer use)'; exit 77 ;;
esac
if test "$2" = git_push; then
    case "$6" in main|master|*:*|+*|-*|'') printf '%s\\n' 'Never: protected or nonliteral push'; exit 77 ;; esac
fi
'''


class HookFailure(PermissionError):
    def __init__(self, feedback, phase):
        self.feedback, self.phase = feedback, phase
        super().__init__('Hook blocked ' + ('execution' if phase == 'before' else 'further calls; action already completed'))


def read_snapshot(path):
    from permissions import parent_fd
    with parent_fd(path) as (directory, name):
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise PermissionError('Hook configuration and scripts must be regular files')
        data = stream.read(16385)
    if len(data) > 16384 or b'\0' in data:
        raise ValueError('Hook file exceeds 16 KiB or contains NUL')
    return data.decode('utf-8')


def load(path):
    """Called only by explicit CLI selection, before any model/tool execution."""
    path = Path(os.path.abspath(os.path.expanduser(os.fspath(path))))
    config = tomllib.loads(read_snapshot(path))
    if set(config) - {'before', 'after', 'timeout'}:
        raise ValueError('Hook config accepts only before, after and timeout')
    timeout = config.get('timeout', 2)
    if type(timeout) is not int or not 1 <= timeout <= 10:
        raise ValueError('Hook timeout must be 1..10 seconds')
    stages = {}
    for phase in ('before', 'after'):
        names = config.get(phase, [])
        if not isinstance(names, list) or len(names) > 4 or any(not isinstance(n, str) or not n for n in names):
            raise ValueError('Each hook stage accepts at most four script paths')
        scripts = [('builtin:never', NEVER)] if phase == 'before' else []
        for name in names:
            script = Path(os.path.expanduser(name))
            script = script if script.is_absolute() else path.parent / script
            scripts.append((str(script), read_snapshot(script)))
        stages[phase] = tuple(scripts)
    return dict(stages, timeout=timeout)


def shell(source, argv, project, timeout):
    from shell_tools import run_bounded
    # Discover this installed Bash's builtins, then disable everything except
    # control/data primitives. In particular: no eval/source/exec/enable escape.
    listing = run_bounded(['/bin/bash', '--noprofile', '--norc', '-p', '-c', 'enable -a'], project, timeout)
    if listing['exit_code'] or listing['timed_out'] or listing['truncated'] or listing['stderr']:
        raise RuntimeError('Cannot establish the hook builtin allow-list')
    lines = listing['stdout'].splitlines()
    if not lines or any(not line.startswith('enable ') for line in lines):
        raise RuntimeError('Unexpected Bash builtin listing')
    builtins = [line.removeprefix('enable ').removeprefix('-n ') for line in lines]
    allowed = {':', '[', 'test', 'printf', 'echo', 'read', 'true', 'false', 'exit', 'break', 'continue'}
    disabled = [name for name in builtins if name not in allowed and name != 'enable']
    prelude = 'set -euf\nenable -n ' + ' '.join(shlex.quote(n) for n in disabled) + '\nenable -n enable\n'
    # ponytail: hooks support builtin-only shell logic; external programs need
    # a separately audited typed operation, never a wider sandbox executable list.
    return run_bounded(['/bin/bash', '--noprofile', '--norc', '-p', '-r', '-c', prelude + source,
                        'kildall-hook', *argv], project, timeout, limit=4096)


def policy_fields(operation, args, project):
    from permissions import guard_path
    from file_tools import path_for
    scope, command, branch = 'outside', '', ''
    if isinstance(args, dict):
        try:
            guard_path(path_for(args['path'], project))
            scope = 'inside'
        except (KeyError, TypeError, ValueError, OSError):
            pass
        try:
            words = shlex.split(args.get('command', ''))
            command = ('git-status' if operation == 'shell' and words == ['git', 'status'] else words[0]) if words else ''
        except (TypeError, ValueError):
            pass
        if isinstance(args.get('branch'), str):
            branch = args['branch'].casefold()
    return scope, command, branch


def run_stage(bundle, phase, operation, arguments, record, project):
    from permissions import decision, execute
    from kildall import strict_json
    args = strict_json(arguments) if isinstance(arguments, str) else arguments
    event = dict(phase=phase, operation=operation, arguments=args,
                 decision=record['id'], status=record['status'], result=record.get('result'))
    encoded = json.dumps(event, ensure_ascii=True)
    feedback = record.setdefault('hook_feedback', [])
    for name, source in bundle[phase]:
        metadata = dict(phase=phase, script=name, sha256=hashlib.sha256(source.encode()).hexdigest(),
                        parent=record['id'], event=event)
        result = None
        try:
            with decision(record['db_path'], project, '_hook', metadata, record['task']) as child:
                if len(encoded) > 65536:
                    raise ValueError('Hook input exceeds 64 KiB')
                # Capability stays in process memory; a model/CLI JSON argument
                # cannot populate this record or create executable hook authority.
                child['hook_capability'] = (source, [phase, operation, encoded,
                    *policy_fields(operation, args, project)], bundle['timeout'])
                result = execute('_hook', {}, child, project)
                child['update'](preview=dict(metadata, output=result))
                if (result['exit_code'] != 0 or result['timed_out'] or result['truncated']
                        or result['stdout'] is None or result['stderr'] is None):
                    raise PermissionError('Hook failed closed')
        except Exception as error:
            feedback.append(dict(source='untrusted_hook', phase=phase, script=name,
                                 output=result, error=str(error)))
            raise HookFailure(feedback, phase) from error
        feedback.append(dict(source='untrusted_hook', phase=phase, script=name, output=result))


def feedback_result(result, record):
    return dict(result=result, hook_feedback=record['hook_feedback']) if record.get('hook_feedback') else result
