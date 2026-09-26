"""Bounded file readers. Authorization stays in permissions.execute."""
import base64
import fnmatch
import os
from pathlib import Path
import stat

from shell_tools import tool, run_bounded

S = dict(type='string')
TOOLS = [
    tool('read_file', 'Read UTF-8 text with line numbers.', dict(path=S, start_line=dict(type='integer', minimum=1), max_lines=dict(type='integer', minimum=1, maximum=200)), ['path']),
    tool('read_bytes', 'Read a byte range; returns base64.', dict(path=S, offset=dict(type='integer', minimum=0), length=dict(type='integer', minimum=1, maximum=8192)), ['path', 'offset', 'length']),
    tool('glob_files', 'Find paths by glob relative to a directory; does not follow symlink directories.', dict(path=S, pattern=S), ['path', 'pattern']),
    tool('grep_files', 'Search regex with optional ripgrep file type (e.g. py).', dict(path=S, pattern=S, file_type=S), ['path', 'pattern']),
    tool('read_pdf', 'Read local PDF text, up to ten pages. Scanned PDFs may have no text.', dict(path=S, start_page=dict(type='integer', minimum=1), pages=dict(type='integer', minimum=1, maximum=10)), ['path']),
    tool('read_image', 'Decode a local image and read text with macOS OCR; scene understanding unavailable.', dict(path=S), ['path']),
    tool('write', 'Write UTF-8 text after user approves the exact diff. Only inside Kildall/code.', dict(path=S, content=S), ['path', 'content']),
    tool('edit', 'Replace exactly one occurrence after user approves the exact diff.', dict(path=S, old=S, new=S), ['path', 'old', 'new']),
]
READS = {item['function']['name'] for item in TOOLS} - {'write', 'edit'}


def path_for(value, project):
    path = Path(os.path.expanduser(value))
    return path if path.is_absolute() else Path(project) / path


def execute(operation, args, project):
    path = path_for(args['path'], project)
    if operation == 'glob_files':
        if Path(args['pattern']).is_absolute() or '..' in Path(args['pattern']).parts:
            raise ValueError('Glob must be relative without parent traversal')
        result, scanned = [], 0
        def failed(error):
            raise error
        # Opening the root distinguishes denial/nonexistence from an empty match set.
        with os.scandir(path):
            pass
        for folder, dirs, files in os.walk(path, followlinks=False, onerror=failed):
            dirs.sort()
            for name in sorted(dirs + files):
                scanned += 1
                candidate = Path(folder) / name
                relative = candidate.relative_to(path).as_posix()
                pattern = args['pattern']
                if Path(relative).match(pattern) or (pattern.startswith('**/') and fnmatch.fnmatchcase(relative, pattern[3:])):
                    result.append(str(candidate))
                if len(result) == 200 or scanned == 10000:
                    return dict(paths=result, truncated=True)
        return dict(paths=result, truncated=False)
    if operation == 'grep_files':
        argv = ['/opt/homebrew/bin/rg', '--json', '--max-count', '200', '--max-filesize', '16M']
        if args.get('file_type'):
            argv += ['--type', args['file_type']]
        argv += ['--', args['pattern'], str(path)]
        result = run_bounded(argv, project, 10, limit=8192)
        if result['exit_code'] not in (0, 1) or result['timed_out']:
            raise OSError(f"grep failed ({result['exit_code']}): {result['stderr']}")
        return result
    if operation == 'read_image':
        from image_reader import read_image
        return read_image(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as source:
        info = os.fstat(source.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise PermissionError('Expected a regular file')
        if operation == 'read_bytes':
            source.seek(args['offset'])
            data = source.read(args['length'])
            return dict(offset=args['offset'], length=len(data), size=info.st_size,
                        encoding='base64', data=base64.b64encode(data).decode())
        if operation == 'read_pdf':
            first, count = args.get('start_page', 1), args.get('pages', 10)
            result = run_bounded(['/opt/homebrew/bin/pdftotext', '-f', str(first), '-l', str(first+count-1),
                                  '-enc', 'UTF-8', '/dev/fd/'+str(source.fileno()), '-'],
                                 project, 20, limit=8192, pass_fds=(source.fileno(),))
            if result['exit_code'] or result['timed_out']:
                raise OSError(f"PDF reader failed ({result['exit_code']}): {result['stderr']}")
            text = dict(text=result['stdout'], truncated=result['truncated'], start_page=first)
            if 'stdout_base64' in result:
                text.update(encoding='base64', data=result['stdout_base64'])
            return text
        first, count = args.get('start_line', 1), args.get('max_lines', 100)
        lines, total, index = [], 0, 0
        while index < first + count - 1:
            raw = source.readline(8193)
            if not raw:
                return dict(text=''.join(lines), truncated=False)
            index += 1
            if index >= first:
                text = raw.decode('utf-8')
                numbered = f'{index}: {text}'
                if total + len(numbered) > 8192:
                    return dict(text=''.join(lines), truncated=True)
                lines.append(numbered)
                total += len(numbered)
            if len(raw) == 8193 and not raw.endswith(b'\n'):
                raise ValueError('Line exceeds8192bytes; use read_bytes')
        return dict(text=''.join(lines), truncated=bool(source.read(1)))
