"""Closed typed action boundary; all tools share one permission path."""

from contextlib import contextmanager
import base64
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import tempfile
import time
import uuid

# Production scope is never supplied by a model, configuration, or command-line flag.
CODE_ROOT = Path.home() / "Orbi" / "code"
COMPUTER_REASON = "Computer input and screen capture are unavailable until Phase 4C"
AUTO = {"read", "ls", "git_status", "remember", "recall", "web_data"}
CONFIRM = {"write", "edit", "commit", "install"}


def guard_path(candidate, root=CODE_ROOT):
    """Expand ~, resolve every candidate, and compare path components, never prefixes."""
    root = Path(root).absolute()
    if os.path.realpath(root) != str(root):
        raise PermissionError("Allowed root must not redirect through a symlink")
    resolved = Path(os.path.realpath(os.path.expanduser(os.fspath(candidate))))
    if not resolved.is_relative_to(root):
        raise PermissionError("Path resolves outside the allowed root")
    return resolved


@contextmanager
def parent_fd(path, root=CODE_ROOT, *, allow_leaf_symlink=False):
    """Anchor mutation to existing, nonsymlink directories; never follow a swapped parent."""
    root = Path(root).absolute()
    candidate = Path(os.path.expanduser(os.fspath(path)))
    guard_path(candidate.parent if allow_leaf_symlink else candidate, root)
    path = Path(os.path.abspath(os.path.expanduser(os.fspath(path))))
    try:
        parts = path.relative_to(root).parts
    except ValueError as error:
        raise PermissionError("Entry itself is outside the allowed root") from error
    if not parts:
        raise PermissionError("This action cannot replace the allowed root")
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = new
        yield fd, parts[-1]
    finally:
        os.close(fd)


def file_bytes(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as source:
        if not stat.S_ISREG(os.fstat(source.fileno()).st_mode):
            raise PermissionError("Expected a regular file")
        return source.read()


def snapshot(path):
    try:
        data = file_bytes(path)
    except FileNotFoundError:
        return None
    info = path.lstat()
    if info.st_nlink != 1:
        raise PermissionError("Hard-linked mutation targets are not supported")
    return data, (info.st_dev, info.st_ino, info.st_mode, info.st_mtime_ns)


def replace_file(path, before, content):
    with parent_fd(path) as (fd, name):
        if snapshot(path) != before:
            raise RuntimeError("Target changed after its diff was approved")
        temporary = ".orbi-write-" + uuid.uuid4().hex
        try:
            out = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          0o600, dir_fd=fd)
            with os.fdopen(out, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                if before:
                    os.fchmod(stream.fileno(), stat.S_IMODE(before[1][2]) & 0o777)
            # Revalidate after writing the temporary file, before publishing it.
            if guard_path(path) != path or snapshot(path) != before:
                raise RuntimeError("Target changed while preparing the approved write")
            os.replace(temporary, name, src_dir_fd=fd, dst_dir_fd=fd)
            check = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=fd)
            with os.fdopen(check, "rb") as stream:
                if stream.read() != content:
                    raise OSError("Write verification failed")
        finally:
            try:
                os.unlink(temporary, dir_fd=fd)
            except FileNotFoundError:
                pass


def exact_diff(path, before, after):
    old = before[0] if before else b""
    result = dict(path=str(path), existed=before is not None,
                  before_sha256=hashlib.sha256(old).hexdigest(),
                  after_sha256=hashlib.sha256(after).hexdigest())
    try:
        a, b = old.decode("utf-8"), after.decode("utf-8")
        result.update(before=a, after=b, diff="".join(difflib.unified_diff(
            a.splitlines(keepends=True), b.splitlines(keepends=True),
            fromfile=str(path), tofile=str(path))))
    except UnicodeDecodeError:
        result.update(encoding="base64", before=base64.b64encode(old).decode(),
                      after=base64.b64encode(after).decode())
    return result


def terminal_confirm(preview, word="yes"):
    # Never consume piped page/model content as approval. No --yes bypass exists.
    with open("/dev/tty", "r") as response, open("/dev/tty", "w") as terminal:
        terminal.write(json.dumps(preview, ensure_ascii=True, indent=2) + "\n")
        terminal.write(f"Type {word!r} to confirm: ")
        terminal.flush()
        return response.readline().rstrip("\r\n") == word


@contextmanager
def decision(db_path, project, operation, arguments, task=None, *, requested=(), hooks=None):
    from orbi import database, process_start
    ident = uuid.uuid4().hex
    row = dict(id=ident, db_path=db_path, task=task, requested=frozenset(requested),
               tier="Never", status="checking", preview=None, reason=None)

    def update(**values):
        row.update(values)
        with database(db_path) as db:
            if db.execute("UPDATE orbi_permissions SET tier=?,status=?,preview=?,reason=?,updated=? WHERE id=?",
                          (row["tier"], row["status"], json.dumps(row["preview"], ensure_ascii=True),
                           row["reason"], time.time(), ident)).rowcount != 1:
                raise RuntimeError("Permission decision disappeared while saving")
    row["update"] = update
    with database(db_path) as db:
        db.execute("INSERT INTO orbi_permissions(id,task,project,operation,arguments,tier,status,pid,owner_start,created,updated) "
                   "VALUES(?,?,?,?,?,'Never','checking',?,?,?,?)",
                   (ident, task, project, operation, json.dumps(arguments, ensure_ascii=True),
                    os.getpid(), process_start(os.getpid()), time.time(), time.time()))
    after_action = False
    try:
        if hooks is not None:
            from hooks import run_stage
            run_stage(hooks, 'before', operation, arguments, row, project)
        yield row
        if hooks is not None:
            after_action = True
            # Save the actual action outcome before post-hooks. Background workers
            # own their action row; hook failures have separate child decisions.
            if row['status'] not in ('rejected', 'authorized', 'done', 'failed', 'timed_out', 'background', 'interrupted'):
                update(status='done')
            run_stage(hooks, 'after', operation, arguments, row, project)
    except BaseException as error:
        if after_action:
            raise  # Preserve the completed/background action and the failed child hook.
        status = "refused" if isinstance(error, PermissionError) else (
            "cancelled" if isinstance(error, (KeyboardInterrupt, EOFError)) else "failed")
        update(status="declined" if row["status"] == "declined" else status, reason=str(error))
        raise
    else:
        if row["status"] not in ("rejected", "authorized", "done", "failed", "timed_out", "background", "interrupted"):
            update(status="done")


def authorize(record, tier, preview=None):
    if tier == 'Confirm' and record['requested'] & {'commit', 'push', 'pr'}:
        preview = dict(preview or {}, user_requested=sorted(record['requested']))
    record["update"](tier=tier, status="waiting" if tier == "Confirm" else "running", preview=preview)
    if tier == "Confirm":
        if not terminal_confirm(preview):
            record["update"](status="declined", reason="User declined")
            raise PermissionError("User declined the exact diff")
        record["update"](status="running")


def fields(args, *names):
    if not isinstance(args, dict) or set(args) != set(names) or any(not isinstance(v, str) for v in args.values()):
        raise ValueError("Expected exactly these string arguments: " + ", ".join(names))


def git_repository(value):
    repo = guard_path(value)
    directory = repo / ".git"
    if not directory.is_dir() or directory.is_symlink():
        raise PermissionError("Expected a local repository with an in-root .git directory")
    if (directory / "commondir").exists():
        raise PermissionError("Redirected Git common directories are not supported")
    for folder, dirs, files in os.walk(directory, followlinks=False, onerror=lambda e: (_ for _ in ()).throw(e)):
        for name in dirs + files:
            path = Path(folder) / name
            guard_path(path)
            if path.is_symlink():
                raise PermissionError("Symlinked Git metadata is not supported")
            if not (path.is_file() or path.is_dir()):
                raise PermissionError("Git metadata must be regular files or directories")
            if path.is_file() and path.stat().st_nlink != 1:
                raise PermissionError("Hard-linked Git metadata is not supported")
    if (directory / "objects/info/alternates").exists():
        raise PermissionError("Redirected Git object stores are not supported")
    # Do not interpret includes or allow repo text to register executable helpers.
    config = subprocess.run(["/opt/homebrew/bin/git", "config", "--file", str(directory / "config"),
        "--no-includes", "--null", "--list"], env={"PATH": "/usr/bin:/bin"},
        capture_output=True, check=True, timeout=10).stdout
    safe = re.compile(r"(?:core\.(?:repositoryformatversion|filemode|bare|logallrefupdates|ignorecase|precomposeunicode|hookspath|fsmonitor|untrackedcache|attributesfile)|user\.(?:name|email)|commit\.gpgsign|diff\.external|gc\.auto|maintenance\.auto|remote\.[^.]+\.(?:url|fetch)|branch\..+\.(?:remote|merge))$")
    for entry in config.split(b"\0"):
        if entry and not safe.fullmatch(entry.split(b"\n", 1)[0].decode()):
            raise PermissionError("Unsupported Git configuration key: " + entry.split(b"\n", 1)[0].decode())
    return repo


def git(repo, *args, index=None):
    # Fixed builtin operations only; no user argv, aliases, shell, hooks, filters or signing.
    env = dict(PATH="/usr/bin:/bin", HOME=str(Path.home()), LANG="C", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL="/dev/null", GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0",
               GIT_DIR=str(repo / ".git"), GIT_WORK_TREE=str(repo), GIT_NO_LAZY_FETCH="1",
               GIT_NO_REPLACE_OBJECTS="1", GIT_ATTR_NOSYSTEM="1", GIT_PAGER="cat")
    if index:
        env["GIT_INDEX_FILE"] = str(index)
    result = subprocess.run(["/opt/homebrew/bin/git", "-c", "core.hooksPath=/dev/null",
        "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false", "-c", "core.attributesFile=/dev/null",
        "-c", "commit.gpgSign=false", "-c", "gc.auto=0", "-c", "maintenance.auto=false",
        "-c", "core.bare=false", "-c", "submodule.recurse=false", *args],
        cwd=repo, env=env, capture_output=True, check=True, timeout=120)
    return result.stdout


def staged(repo):
    head = git(repo, "rev-parse", "--verify", "HEAD").decode().strip()
    branch = git(repo, "symbolic-ref", "HEAD").decode().strip()
    if not branch.startswith("refs/heads/"):
        raise PermissionError("Commit requires a local branch")
    index = file_bytes(repo / ".git/index")
    diff = git(repo, "diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv", "--no-renames",
               "--no-color", "--ignore-submodules=none", "--submodule=short", head, "--")
    for name in git(repo, "diff", "--cached", "--name-only", "--ignore-submodules=none", "-z", head, "--").split(b"\0"):
        if name:
            guard_path(repo / os.fsdecode(name))
    if not diff:
        raise ValueError("No staged changes")
    if file_bytes(repo / ".git/index") != index or git(repo, "rev-parse", "HEAD").decode().strip() != head:
        raise RuntimeError("Staged changes moved while preparing the diff")
    return head, branch, index, diff


def execute(operation, args, record, project):
    """The sole permission boundary; unknown names and command forms fail closed."""
    if operation == '_hook':
        fields(args)
        if 'hook_capability' not in record:
            raise PermissionError('Hooks require explicit configuration; not a model tool')
        from hooks import shell
        source, argv, timeout = record.pop('hook_capability')
        authorize(record, 'Auto')
        return shell(source, argv, project, timeout)
    if operation == "shell":
        fields(args, "command")
        parts = shlex.split(args["command"])
        if parts == ["git", "status"]:
            operation, args = "git_status", {"path": project}
        elif len(parts) in (1, 2) and parts[0] == "ls":
            operation, args = "ls", {"path": parts[1] if len(parts) == 2 else project}
        elif len(parts) == 2 and parts[0] == "cat":
            operation, args = "read", {"path": parts[1]}
        else:
            operation = "run_command"
    import file_tools
    import shell_tools
    import git_tools
    import instruction_skills
    from tool_grammar import validate_arguments
    definition = next((tool['function'] for tool in file_tools.TOOLS + shell_tools.TOOLS + git_tools.TOOLS + [instruction_skills.TOOL]
                       if tool['function']['name'] == operation), None)
    if definition:
        validate_arguments(definition['parameters'], args)
    if operation in git_tools.NAMES:
        return git_tools.execute(operation, args, record, project)
    if operation in ('skills', 'load_skill'):
        if operation == 'skills':
            fields(args)
        from orbi import TOOLS
        authorize(record, 'Auto')
        available = {t['function']['name'] for t in TOOLS}
        return (instruction_skills.discover(project, available) if operation == 'skills' else
                instruction_skills.load(args['name'], project, available))
    if operation in ('run_command', 'shell_job'):
        return shell_tools.execute(operation, args, record, project)
    if operation in file_tools.READS:
        authorize(record, 'Auto')
        return file_tools.execute(operation, args, project)
    if operation in ('write', 'edit'):
        args = dict(args, path=str(file_tools.path_for(args['path'], project)))
    if operation in ("read", "ls"):
        fields(args, "path")
        path = Path(os.path.expanduser(args["path"]))
        authorize(record, "Auto")
        if operation == "read":
            return {"text": file_bytes(path).decode("utf-8")}
        # scandir raises on denied access; an empty list means a successful read.
        with os.scandir(path) as entries:
            return {"entries": sorted(entry.name for entry in entries)}
    if operation == "git_status":
        fields(args, "path")
        repo = git_repository(args["path"])
        authorize(record, "Auto")
        return {"status": git(repo, "status", "--porcelain=v1", "--ignore-submodules=all").decode()}
    if operation in ("write", "edit", "install"):
        fields(args, *(('path', 'old', 'new') if operation == "edit" else
                       ('source', 'path') if operation == "install" else ('path', 'content')))
        path = guard_path(args["path"])
        if ".git" in (part.casefold() for part in path.relative_to(CODE_ROOT).parts):
            raise PermissionError("Git metadata may only be changed by the commit operation")
        before = snapshot(path)
        if operation == "edit":
            if before is None or not args["old"] or before[0].decode("utf-8").count(args["old"]) != 1:
                raise ValueError("Edit requires exactly one matching nonempty old string")
            content = before[0].decode("utf-8").replace(args["old"], args["new"], 1).encode()
        elif operation == "install":
            # ponytail: install a local artifact only; package hooks need Phase 4 confinement.
            content = file_bytes(Path(os.path.expanduser(args["source"])))
        else:
            content = args["content"].encode("utf-8")
        authorize(record, "Confirm", exact_diff(path, before, content))
        replace_file(path, before, content)
        return {"path": str(path), "sha256": hashlib.sha256(content).hexdigest()}
    if operation == "commit":
        if 'commit' not in record['requested']:
            raise PermissionError("Commit requires explicit user intent")
        fields(args, "path", "message")
        repo = git_repository(args["path"])
        before = staged(repo)
        head, branch, index, diff = before
        authorize(record, "Confirm", dict(repository=str(repo), parent=head, branch=branch,
            message=args["message"], diff=diff.decode("utf-8", errors="surrogateescape")))
        if git_repository(repo) != repo or staged(repo) != before:
            raise RuntimeError("Staged diff changed after approval")
        # Freeze the approved index; update-ref compares the reviewed parent atomically.
        with tempfile.TemporaryDirectory(prefix="orbi-index-", dir=repo / ".git") as directory:
            private = Path(directory) / "index"
            private.write_bytes(index)
            tree = git(repo, "write-tree", index=private).decode().strip()
            commit = git(repo, "commit-tree", tree, "-p", head, "-m", args["message"]).decode().strip()
            git(repo, "update-ref", "--no-deref", "-m", "orbi: approved commit", branch, commit, head)
        if git(repo, "rev-parse", branch).decode().strip() != commit:
            raise OSError("Commit verification failed")
        return {"commit": commit}
    if operation == "web_data":
        fields(args, "text")
        authorize(record, "Auto")
        # A data-only value: never parse its contents as actions, roles, or approval.
        return {"source": "untrusted_web", "text": args["text"]}
    raise PermissionError("Action is outside the closed executor; " + COMPUTER_REASON)


def run_action(db_path, project, operation, raw_args, task=None, *, hooks=None):
    from orbi import strict_json
    # This entry point is a direct user CLI action, never a model/skill dispatch.
    requested = (operation.removeprefix('git_'),) if task is None else ()
    with decision(db_path, project, operation, raw_args, task, requested=requested, hooks=hooks) as record:
        args = strict_json(raw_args) if isinstance(raw_args, str) else raw_args
        result = execute(operation, args, record, project)
        record['result'] = result
    from hooks import feedback_result
    return feedback_result(result, record)


def nuke_manifest(root=CODE_ROOT):
    """Postorder entries; a symlink is an entry to unlink, never a directory to visit."""
    root = Path(root).absolute()
    guard_path(root, root)
    paths = []
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW

    def visit(path, fd):
        guard_path(path, root)
        info = os.fstat(fd)
        with os.scandir(fd) as entries:
            names = sorted(entry.name for entry in entries)
        for name in names:
            child = path / name
            # Validate the entry's own location and its parent, not a symlink's target.
            if not child.is_absolute() or not child.is_relative_to(root):
                raise PermissionError("Deletion entry is outside the allowed root")
            guard_path(child.parent, root)
            item = os.lstat(name, dir_fd=fd)
            if stat.S_ISDIR(item.st_mode):
                guard_path(child, root)
                nested = os.open(name, flags, dir_fd=fd)
                try:
                    opened = os.fstat(nested)
                    if (opened.st_dev, opened.st_ino) != (item.st_dev, item.st_ino):
                        raise RuntimeError("Deletion directory changed while scanning")
                    visit(child, nested)
                finally:
                    os.close(nested)
            else:
                if not stat.S_ISLNK(item.st_mode):
                    guard_path(child, root)
                paths.append((str(child), item.st_dev, item.st_ino, item.st_mode))
        paths.append((str(path), info.st_dev, info.st_ino, info.st_mode))

    fd = os.open(root, flags)
    try:
        visit(root, fd)
    finally:
        os.close(fd)
    return paths, 0


def _delete_tree(root, manifest):
    """Internal deletion primitive; tests supply a throwaway tree, CLI always CODE_ROOT."""
    root = Path(root).absolute()
    fresh, rejected = nuke_manifest(root)
    if rejected or fresh != manifest:
        raise PermissionError("Deletion tree changed or contains an unsafe path")
    for name, dev, ino, mode in manifest:
        path = Path(name)
        if path == root:
            guard_path(root, root)
            fd = os.open(root.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            try:
                info = os.lstat(root.name, dir_fd=fd)
                if (info.st_dev, info.st_ino, info.st_mode) != (dev, ino, mode):
                    raise RuntimeError("Deletion root changed")
                os.rmdir(root.name, dir_fd=fd)
            finally:
                os.close(fd)
        else:
            with parent_fd(path, root, allow_leaf_symlink=stat.S_ISLNK(mode)) as (fd, leaf):
                info = os.lstat(leaf, dir_fd=fd)
                if (info.st_dev, info.st_ino, info.st_mode) != (dev, ino, mode):
                    raise RuntimeError("Deletion candidate changed")
                (os.rmdir if stat.S_ISDIR(mode) else os.unlink)(leaf, dir_fd=fd)
        if os.path.lexists(path):
            raise OSError("Deletion verification failed")


def nuke_database(root=CODE_ROOT):
    guard_path(root, root)
    path = Path(root) / "orbi.db"
    for suffix in ("", "-wal", "-shm", "-journal"):
        candidate = Path(str(path) + suffix)
        guard_path(candidate, root)
        if os.path.lexists(candidate):
            info = candidate.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise PermissionError("Nuke audit database and sidecars must be regular unlinked files")
    return path


def nuke(*, delete=False):
    from orbi import initialize
    db_path = nuke_database()
    initialize(db_path)
    with decision(db_path, str(Path.cwd().resolve()), "nuke", {"delete": delete}) as record:
        paths, rejected = nuke_manifest()
        report = dict(operation="nuke", decision=record["id"], root=str(CODE_ROOT), dry_run=not delete,
                      paths=[row[0] for row in paths], rejected_outward_paths=rejected)
        print(json.dumps(report, ensure_ascii=True, indent=2), flush=True)
        record["update"](tier="Confirm" if delete else "Auto", preview=report)
        if not delete:
            return report
        if rejected:
            record["update"](tier="Never")
            raise PermissionError("Nuke refused: scan contains unsafe paths")
        record["update"](status="waiting")
        if not terminal_confirm(report, "orbi"):
            record["update"](status="declined")
            raise PermissionError("Nuke declined")
        record["update"](status="authorized")
    # Nuke intentionally removes its own database. Emit the final audit to stdout;
    # the pre-deletion decision remains inspectable there even after the directory is gone.
    try:
        _delete_tree(CODE_ROOT, paths)
    except BaseException as error:
        if db_path.is_file():
            record["update"](status="failed", reason=str(error))
        print(json.dumps(dict(operation="nuke", decision=record["id"], status="failed", reason=str(error))), flush=True)
        raise
    print(json.dumps(dict(operation="nuke", decision=record["id"], status="done", root=str(CODE_ROOT))), flush=True)
    return report
