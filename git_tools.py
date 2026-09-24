"""Typed Git operations, dispatched and approved only by permissions.execute."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from shell_tools import tool

PATH = dict(type='string')
TOOLS = [
    tool('git_read', 'Read Git status, diff or log without approval. Diff returns the review hash required by commit.',
         dict(path=PATH, action=dict(type='string', enum=['status', 'diff', 'log']), staged=dict(type='boolean')), ['path', 'action']),
    tool('git_branch', 'Create a branch at HEAD, with approval.', dict(path=PATH, name=PATH), ['path', 'name']),
    tool('git_switch', 'Switch a clean worktree to an existing branch, with approval.', dict(path=PATH, name=PATH), ['path', 'name']),
    tool('git_commit', 'Commit only on explicit user request. Write message from git_read staged diff and supply its hash.',
         dict(path=PATH, message=PATH, diff_sha256=PATH), ['path', 'message', 'diff_sha256']),
    tool('git_push', 'Push one feature branch to origin with approval. Main/master and force are forbidden.',
         dict(path=PATH, branch=PATH), ['path', 'branch']),
    tool('git_pr', 'On explicit user request, open a GitHub PR for an already pushed branch, with approval.',
         dict(path=PATH, branch=PATH, base=PATH, title=PATH, body=PATH), ['path', 'branch', 'base', 'title', 'body']),
]
NAMES = {t['function']['name'] for t in TOOLS}
DIFF = ('--binary', '--no-ext-diff', '--no-textconv', '--no-renames', '--no-color',
        '--ignore-submodules=none', '--submodule=short')


def branch_name(name):
    # Deliberately accept simple local branch names, not Git revision expressions.
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/-]{0,199}', name) or any(
            part in ('', '.', '..') or part.startswith('.') or part.endswith(('.', '.lock'))
            for part in name.split('/')) or '..' in name or name == 'HEAD':
        raise ValueError('Expected a literal local branch name')
    return 'refs/heads/' + name


def feature(name):
    ref = branch_name(name)
    if name.casefold() in ('main', 'master'):
        raise PermissionError('Pushing to main or master is Never tier')
    return ref


def revision(repo, ref):
    from permissions import git
    return git(repo, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()


def origin(repo):
    from permissions import file_bytes, git, guard_path
    values = git(repo, 'config', '--local', '--get-all', 'remote.origin.url').decode().splitlines()
    if len(values) != 1:
        raise PermissionError('Origin must have exactly one URL')
    value = values[0]
    match = re.fullmatch(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?', value)
    if match and all(s not in ('.', '..') for s in match.groups()):
        return value, '/'.join(match.groups())
    # ponytail: GitHub HTTPS and in-root bare remotes only; add a transport after auditing its helpers.
    path = Path(value)
    if not path.is_absolute():
        raise PermissionError('Origin requires GitHub HTTPS or an absolute in-root bare repository')
    path = guard_path(path)
    if not (path / 'HEAD').is_file() or not (path / 'objects').is_dir():
        raise PermissionError('Local origin must be a bare repository')
    if any(os.path.lexists(path / name) for name in ('.git', 'commondir', 'objects/info/alternates')):
        raise PermissionError('Redirected local remote stores are forbidden')
    for folder, dirs, files in os.walk(path, followlinks=False, onerror=lambda e: (_ for _ in ()).throw(e)):
        for name in dirs + files:
            entry = Path(folder) / name
            guard_path(entry)
            if entry.is_symlink() or (entry.is_file() and entry.stat().st_nlink != 1):
                raise PermissionError('Redirected remote metadata is forbidden')
            if not (entry.is_file() or entry.is_dir()):
                raise PermissionError('Remote metadata must be regular files or directories')
            # Local receive-pack does not inherit the client's -c hooksPath setting.
            if entry.parent == path / 'hooks' and entry.is_file() and not entry.name.endswith('.sample'):
                raise PermissionError('Local remote hooks are unsupported')
            if path / 'refs' in entry.parents and entry.is_file() and file_bytes(entry).startswith(b'ref:'):
                raise PermissionError('Symbolic remote refs can redirect a feature push and are forbidden')
    config = subprocess.run(['/opt/homebrew/bin/git', 'config', '--file', str(path / 'config'),
        '--no-includes', '--null', '--list'], capture_output=True, check=True, timeout=10,
        env={'PATH': '/usr/bin:/bin'}).stdout
    allowed = {'core.repositoryformatversion', 'core.filemode', 'core.bare', 'core.logallrefupdates',
               'core.ignorecase', 'core.precomposeunicode'}
    if any(entry and entry.split(b'\n', 1)[0].decode() not in allowed for entry in config.split(b'\0')):
        raise PermissionError('Unsupported local remote configuration')
    values = {entry.partition(b'\n')[0]: entry.partition(b'\n')[2] for entry in config.split(b'\0') if entry}
    if values.get(b'core.bare') != b'true':
        raise PermissionError('Local origin must declare core.bare=true')
    return str(path), None


def transport(repo, *args):
    from permissions import git
    return git(repo, '-c', 'protocol.allow=never', '-c', 'protocol.https.allow=always',
        '-c', 'protocol.file.allow=always', '-c', 'credential.helper=',
        '-c', 'credential.https://github.com.helper=!/opt/homebrew/bin/gh auth git-credential', *args)


def remote_head(repo, url, ref):
    rows = transport(repo, 'ls-remote', '--refs', '--', url, ref).decode().splitlines()
    if not rows:
        return None
    if len(rows) != 1 or rows[0].split('\t')[1] != ref:
        raise RuntimeError('Unexpected remote ref response')
    return rows[0].split('\t')[0]


def create_pr(repository, payload):
    # API only: unlike gh pr create, this cannot auto-push or create a fork.
    env = {k: v for k, v in os.environ.items() if k in ('HOME', 'GH_TOKEN', 'GITHUB_TOKEN')}
    env.update(PATH='/usr/bin:/bin', GH_PROMPT_DISABLED='1', GH_HOST='github.com')
    result = subprocess.run(['/opt/homebrew/bin/gh', 'api', '--hostname', 'github.com',
        'repos/' + repository + '/pulls', '--method', 'POST', '--input', '-'],
        input=json.dumps(payload).encode(), capture_output=True, check=True, timeout=120, env=env)
    return json.loads(result.stdout)


def execute(operation, args, record, project):
    from permissions import authorize, execute as dispatch, git, git_repository, guard_path, staged
    path = Path(os.path.expanduser(args['path']))
    repo = git_repository(path if path.is_absolute() else Path(project) / path)
    if operation == 'git_read':
        authorize(record, 'Auto')
        action = args['action']
        if action == 'status':
            return dict(status=git(repo, 'status', '--porcelain=v1', '--ignore-submodules=all').decode())
        if action == 'log':
            return dict(log=git(repo, 'log', '-20', '--no-show-signature', '--no-decorate',
                '--format=%h %s', '--').decode())
        cached = args.get('staged', False)
        if not cached and (any(e.startswith(b'160000 ') for e in git(repo, 'ls-files', '--stage', '-z').split(b'\0'))
                           or any(e.startswith(b'160000 ') for e in git(repo, 'ls-tree', '-rz', 'HEAD').split(b'\0'))):
            raise PermissionError('Submodule worktree diff is unsupported; use staged diff for exact gitlink changes')
        diff = git(repo, 'diff', *(['--cached'] if cached else []), *DIFF, 'HEAD', '--')
        digest = hashlib.sha256(diff).hexdigest()
        record['update'](preview=dict(repository=str(repo), staged=cached, diff_sha256=digest))
        return dict(diff=diff.decode('utf-8', errors='surrogateescape'), diff_sha256=digest)
    if operation == 'git_commit':
        if 'commit' not in record['requested']:
            raise PermissionError('Commit requires --git commit or a direct user tool invocation')
        if not args['message'].strip() or '\0' in args['message']:
            raise ValueError('Expected a nonempty commit message')
        diff = staged(repo)[3]
        if hashlib.sha256(diff).hexdigest() != args['diff_sha256']:
            raise PermissionError('Commit must refer to the current real staged diff')
        if record['task'] is not None:
            from orbi import database
            with database(record['db_path']) as db:
                seen = db.execute("SELECT preview FROM orbi_permissions WHERE task=? AND operation='git_read' AND status='done'",
                                  (record['task'],)).fetchall()
            required = dict(repository=str(repo), staged=True, diff_sha256=args['diff_sha256'])
            if not any(json.loads(row[0]) == required for row in seen if row[0]):
                raise PermissionError('Read the real staged diff before writing a commit message')
        return dispatch('commit', dict(path=str(repo), message=args['message']), record, project)
    if operation in ('git_branch', 'git_switch'):
        ref = branch_name(args['name'])
        head = revision(repo, 'HEAD')
        if operation == 'git_branch':
            authorize(record, 'Confirm', dict(repository=str(repo), create=ref, commit=head))
            git_repository(repo)
            if revision(repo, 'HEAD') != head:
                raise RuntimeError('HEAD changed after approval')
            git(repo, 'update-ref', '--no-deref', ref, head, '0' * len(head))
            if revision(repo, ref) != head:
                raise OSError('Branch verification failed')
            return dict(branch=args['name'], commit=head)
        target = revision(repo, ref)
        def clean():
            if any(e and (e[:1].islower() or e[:1] == b'S') for e in git(repo, 'ls-files', '-v', '-z').split(b'\0')):
                raise PermissionError('Switch refuses assume-unchanged or skip-worktree index entries')
            if any(e.startswith(b'160000 ') for e in git(repo, 'ls-files', '--stage', '-z').split(b'\0')):
                raise PermissionError('Switching submodule indexes is unsupported')
            for rev in (head, target):
                for entry in git(repo, 'ls-tree', '-rz', rev).split(b'\0'):
                    if entry:
                        meta, name = entry.split(b'\t', 1)
                        if meta.split()[0] not in (b'100644', b'100755'):
                            raise PermissionError('Switching symlink or submodule trees is unsupported')
                        path = guard_path(repo / os.fsdecode(name))
                        if not path.is_relative_to(repo) or any(part.casefold() == '.git' for part in Path(os.fsdecode(name)).parts):
                            raise PermissionError('Tree path escapes its worktree')
                        if path.exists() and path.stat().st_nlink != 1:
                            raise PermissionError('Hard-linked worktree files cannot be switched')
            if git(repo, 'status', '--porcelain=v1', '--untracked-files=all', '--ignore-submodules=none'):
                raise PermissionError('Switch requires a clean worktree, including untracked files')
        clean()
        diff = git(repo, 'diff', *DIFF, head, target, '--').decode('utf-8', errors='surrogateescape')
        authorize(record, 'Confirm', dict(repository=str(repo), switch=ref, parent=head, target=target, diff=diff))
        git_repository(repo)
        if revision(repo, 'HEAD') != head or revision(repo, ref) != target:
            raise RuntimeError('Branch changed after approval')
        clean()
        git(repo, 'switch', '--no-guess', '--no-overwrite-ignore', '--no-recurse-submodules', args['name'])
        if git(repo, 'symbolic-ref', 'HEAD').decode().strip() != ref or revision(repo, 'HEAD') != target:
            raise OSError('Switch verification failed')
        return dict(branch=args['name'], commit=target)
    ref = feature(args['branch'])
    required = operation.removeprefix('git_')
    if required not in record['requested']:
        raise PermissionError(f'{required} requires explicit user intent')
    head = revision(repo, ref)
    destination, repository = origin(repo)
    old = remote_head(repo, destination, ref)
    if operation == 'git_push':
        # The single refspec contains a pinned commit and an allow-listed destination.
        preview = dict(repository=str(repo), destination=destination, ref=ref, before=old, after=head)
        # Empty-tree diff for a new ref shows every published file, not just the last commit.
        before = old or '4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        preview['diff'] = git(repo, 'diff', *DIFF, before, head, '--').decode('utf-8', errors='surrogateescape')
        preview['commits'] = git(repo, 'log', '--no-show-signature', '--format=%H %s',
                                head if old is None else old + '..' + head, '--').decode('utf-8', errors='surrogateescape')
        authorize(record, 'Confirm', preview)
        git_repository(repo)
        if origin(repo)[0] != destination or revision(repo, ref) != head or remote_head(repo, destination, ref) != old:
            raise RuntimeError('Push changed after approval')
        output = transport(repo, 'push', '--porcelain', '--no-verify', '--no-follow-tags', '--', destination, head + ':' + ref).decode()
        if remote_head(repo, destination, ref) != head:
            raise OSError('Remote push verification failed')
        return dict(branch=args['branch'], commit=head, output=output)
    if repository is None:
        raise PermissionError('PR creation requires a GitHub HTTPS origin')
    if old != head:
        raise PermissionError('Push this exact head explicitly before requesting a PR')
    base_ref = branch_name(args['base'])
    base = remote_head(repo, destination, base_ref)
    if base is None or base_ref == ref or not args['title'].strip():
        raise ValueError('PR requires an existing distinct base and a nonempty title')
    diff = git(repo, 'diff', *DIFF, base + '...' + head, '--').decode('utf-8', errors='surrogateescape')
    payload = dict(head=args['branch'], base=args['base'], title=args['title'], body=args['body'])
    authorize(record, 'Confirm', dict(repository=repository, payload=payload, head=head, base=base, diff=diff))
    git_repository(repo)
    if origin(repo)[0] != destination or remote_head(repo, destination, ref) != head or remote_head(repo, destination, base_ref) != base:
        raise RuntimeError('PR refs changed after approval')
    result = create_pr(repository, payload)
    if result['head']['sha'] != head or result['base']['sha'] != base or result['head']['ref'] != args['branch'] or result['base']['ref'] != args['base'] or not result['html_url'].startswith('https://github.com/' + repository + '/pull/'):
        raise RuntimeError('PR API returned a different pull request; inspect the remote result')
    return dict(url=result['html_url'], number=result['number'])
