"""Rename compatibility: one module state and a consistent backup interpreter."""

from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
from unittest.mock import patch

import kildall
import orbi


def main():
    assert orbi is kildall
    with patch.object(orbi, 'strict_json', return_value='shared'):
        assert kildall.strict_json('{}') == 'shared'
    # Direct script execution must not create a second module when tools import it.
    probe = '''import argparse, runpy, sys
from pathlib import Path
script=Path(sys.argv[1])
sys.path.insert(0,str(script.parent))
def check(self,*args,**kwargs):
    import kildall, orbi
    assert kildall is orbi is sys.modules['__main__']
    raise SystemExit(0)
argparse.ArgumentParser.parse_args=check
runpy.run_path(str(script),run_name='__main__')
'''
    subprocess.run([sys.executable, '-c', probe, str(kildall.ROOT / 'kildall.py')],
                   cwd=tempfile.gettempdir(), check=True)
    with tempfile.TemporaryDirectory(prefix='kildall-rename-') as temporary:
        root = Path(temporary).resolve()
        config = (kildall.ROOT / 'kildall.toml').read_text()
        legacy = root / 'legacy.toml'
        modern = root / 'modern.toml'
        legacy.write_text(config.replace('kildall.db', 'legacy.sqlite3'))
        modern.write_text(config.replace('kildall.db', 'modern.sqlite3'))
        with patch.dict(os.environ, {'ORBI_CONFIG': str(legacy)}, clear=True):
            assert orbi.settings()['paths']['db_path'] == root / 'legacy.sqlite3'
            with patch.dict(os.environ, {'KILDALL_CONFIG': str(modern)}):
                assert orbi.settings() == kildall.settings()
                assert kildall.settings()['paths']['db_path'] == root / 'modern.sqlite3'
        binary = root / 'python3.12'
        binary.write_bytes(b'fixture interpreter; never executed')
        (root / 'python').symlink_to(binary.name)
        with patch.object(sys, 'executable', str(binary)), \
             patch.dict(os.environ, {'KILDALL_CONFIG': str(modern)}), \
             patch('backup_ops.schedule_backups') as register, \
             redirect_stdout(io.StringIO()):
            kildall.schedule_backups({'paths': {'code_dir': root}})
            register.assert_called_once_with({'paths': {'code_dir': root}}, kildall.ROOT, str(binary))
            from backup_ops import backup_payload
            schedule = backup_payload({'paths': {'code_dir': root}}, kildall.ROOT, binary)
        assert schedule['ProgramArguments'] == [str(root / 'python'), str(kildall.ROOT / 'kildall.py'), '--backup']
        assert schedule['EnvironmentVariables'] == {'KILDALL_CONFIG': str(modern)}
        assert schedule['Label'] == 'local.kildall.backup'
        assert schedule['RunAtLoad'] is True
    print('PASS: shared alias/script state, legacy config fallback, new config precedence, canonical backup interpreter')


if __name__ == '__main__':
    main()
