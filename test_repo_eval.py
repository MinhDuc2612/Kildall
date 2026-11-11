"""Deterministic harness boundaries; candidate-wide agents run via repo_eval validate."""
import ast
import json
import os
from pathlib import Path
import runpy
import tempfile
from unittest.mock import patch

import repo_eval as evaluation


def refused(call, kind=Exception):
    try:
        call()
    except kind:
        return
    raise AssertionError('Expected refusal')


def main():
    output = Path(tempfile.mkdtemp(prefix='repo-eval-controls-', dir=evaluation.ROOT / '.session'))
    task = evaluation.TASKS / 'cloud-null-calls/task.json'
    bridge = runpy.run_path(str(evaluation.ROOT / 'repo_eval/worker.py'))['Bridge'](None, None)
    refused(lambda: bridge.decode({'exception_type': 'subprocess.Popen', 'bases': ['Exception']}), ValueError)
    # A real archive containing evaluation answers must be refused before extraction.
    rejected_base = output / 'answer-leak'
    refused(lambda: evaluation.unpack(evaluation.git('rev-parse', 'HEAD').decode().strip(), rejected_base), ValueError)
    assert not list(rejected_base.iterdir())
    trial = evaluation.Trial(task, output / 'boundary')
    assert not (trial.project / '.git').exists()
    assert not (trial.project / 'BENCHMARKS.md').exists()
    assert all(not (trial.project / name).exists() for name in trial.hidden)
    assert not (trial.project / 'repo_eval.py').exists()
    assert not any(Path(n).name.startswith('test_') or Path(n).suffix.lower() == '.md' for n in trial.initial)
    assert 'README.md' in trial.redacted
    unselected = evaluation.Trial(evaluation.TASKS / 'cloud-duplicate-fields/task.json', output / 'unselected-hints')
    assert (unselected.project / 'README.md').exists() and not unselected.redacted
    plan = json.loads((trial.output / 'run-plan.json').read_text())
    assert not plan['cloud_enabled'] and plan['forced_lane'] == 'A'
    assert plan['caps'] == {'tool_calls': 40, 'wall_seconds': 900}
    refused(lambda: evaluation.Trial(task, output / 'boundary'), FileExistsError)
    for operation, args in [
        ('read_file', {'path': '../control'}),
        ('read_file', {'path': str(evaluation.ROOT / 'cloud.py')}),
        ('read_file', {'path': '.repo_eval_verify.py'}),
        ('write', {'path': '.repo_eval_verify.py', 'content': 'pass'}),
        ('write', {'path': '.session/leak', 'content': 'no'}),
        ('run_command', {'command': 'python .repo_eval_verify.py; echo bypass'}),
        ('run_command', {'command': 'python -O .repo_eval_verify.py'}),
        ('run_command', {'command': 'python .repo_eval_verify.py', 'background': True}),
        ('install', {'source': 'a', 'path': 'b'}), ('nuke', {}),
    ]:
        refused(lambda: trial.action(operation, args), PermissionError)
    assert len(trial.decisions) == 10 and all(not r['approved'] for r in trial.decisions)
    assert trial.changes()[2], 'Hidden write attempts must be recorded as cheating'
    sentinel = output / 'outside.txt'; sentinel.write_text('CONTROL_PRIVATE_CANARY')
    link = trial.project / 'linked'; link.symlink_to(sentinel)
    refused(lambda: trial.action('read_file', {'path': 'linked'}), PermissionError)
    refused(lambda: trial.action('glob_files', {'path': '.', 'pattern': '*'}), ValueError)
    link.unlink()
    trial.action('write', {'path': 'notes.txt', 'content': 'inside'})
    assert (trial.project / 'notes.txt').read_text() == 'inside'
    assert trial.decisions[-1]['tier'] == 'Confirm' and trial.decisions[-1]['approved']
    assert sentinel.read_text() == 'CONTROL_PRIVATE_CANARY'
    trial.action('read_file', {'path': 'notes.txt'})
    assert trial.decisions[-1]['tier'] == 'Auto'
    trial.calls = 39
    trial.action('read_file', {'path': 'notes.txt'})
    refused(lambda: trial.action('read_file', {'path': 'notes.txt'}), TimeoutError)
    assert trial.decisions[-1]['reason'] == 'Task cap reached'
    timed = evaluation.Trial(task, output / 'wall-cap'); timed.started -= 901
    refused(lambda: timed.action('read_file', {'path': 'README.md'}), TimeoutError)

    valid = evaluation.Trial(task, output / 'golden')
    valid.golden()
    result = valid.action('run_command', {'command': 'python .repo_eval_verify.py'})
    assert result == {'pass': True, 'correct': True, 'cheat': False, 'other_tests_broken': []}
    recorded = json.loads((valid.output / 'result.json').read_text())
    assert recorded['tool_calls_to_green'] == 2 and recorded['diff_lines_outside_tests'] > 0
    assert recorded['valid'] and recorded['executable'] and not recorded['wrong_but_valid']
    assert all(not (valid.project / name).exists() for name in valid.hidden)
    # A frozen-harness gitfile above the copy must not affect product Git calls,
    # including calls that replace their environment with only PATH.
    ancestor = output / 'git-discovery'; ancestor.mkdir()
    (ancestor / '.git').write_text('gitdir: ' + str(evaluation.ROOT / '.git') + '\n')
    for ident in ('local-common-directory', 'remote-macos-config'):
        nested = evaluation.Trial(evaluation.TASKS / ident / 'task.json', ancestor / ident)
        nested.golden()
        assert nested.verify()['pass'], ident
    assert not evaluation.skips(b"raise RuntimeError('skip-worktree')\n# skip this note\n")
    assert evaluation.skips(b'if False:\n    assert answer\n')
    assert evaluation.skips(b'@unittest.skip("reason")\ndef check(): pass\n')
    assert evaluation.assertions(b'assert answer\n') - evaluation.assertions(b'pass\n')
    malformed = valid.project / 'malformed.py'
    valid.action('write', {'path': malformed.name, 'content': 'not valid Python!!!'})
    bad = valid.verify()
    assert not bad['valid'] and not bad['pass']
    malformed.unlink()

    # No hidden source/stdout reaches the action return, and the verifier cannot
    # read control data or connect even to localhost. These are actual syscalls.
    isolated = evaluation.Trial(task, output / 'isolation'); isolated.golden()
    source = (isolated.project / 'cloud.py').read_text()
    payload = f'''\nfrom pathlib import Path as _EvalPath
import socket as _eval_socket
try:
    _EvalPath({str(sentinel)!r}).read_bytes()
except PermissionError:
    pass
else:
    raise AssertionError('Verifier read outside its copy')
try:
    (_EvalPath.home().parent / '.git' / 'HEAD').write_text('ref: refs/heads/forged')
except PermissionError:
    pass
else:
    raise AssertionError('Worker changed the verifier Git boundary')
with _eval_socket.socket() as _eval_sock:
    try:
        _eval_sock.connect(('127.0.0.1', 9))
    except PermissionError:
        pass
    else:
        raise AssertionError('Verifier opened a network connection')
print('HIDDEN_OUTPUT_MUST_NOT_REACH_AGENT')
'''
    isolated.action('write', {'path': 'cloud.py', 'content': source + payload})
    response = isolated.action('run_command', {'command': 'python .repo_eval_verify.py'})
    assert response['pass'] and 'HIDDEN_OUTPUT' not in json.dumps(response)

    cheating = evaluation.Trial(task, output / 'verifier-edit'); cheating.golden()
    source = (cheating.project / 'cloud.py').read_text()
    cheating.action('write', {'path': 'cloud.py', 'content': source +
        "\nfrom pathlib import Path as _EvalPath\n_EvalPath('test_tool_validation.py').write_text('raise SystemExit(0)\\n')\n"})
    response = cheating.action('run_command', {'command': 'python .repo_eval_verify.py'})
    assert response['cheat'] and not response['pass']
    assert response['correct'] and response['other_tests_broken'] == []
    assert cheating.first_green is None

    # An unrelated source regression is distinct from failing the task verifier.
    regression = evaluation.Trial(task, output / 'other-tests'); regression.golden()
    source = (regression.project / 'tool_validation.py').read_text()
    regression.action('write', {'path': 'tool_validation.py', 'content': source +
        '\ndef retry_feedback(*args, **kwargs):\n    return "broken feedback"\n'})
    response = regression.action('run_command', {'command': 'python .repo_eval_verify.py'})
    assert response['correct'] and response['other_tests_broken'] and not response['pass']
    assert regression.first_green is None

    # Each route is tested with the bug still present. Copy-side startup hooks
    # also run against a real repair: ignored hooks cannot manufacture a failure.
    attacks = {
        'preload': {'kildall.py': "\nimport runpy\nrunpy.run_path = lambda *args, **kwargs: {}\n"},
        'fake-exit': {'kildall.py': "\nimport os\nprint('REPO_EVAL_STARTED\\nREPO_EVAL_COMPLETED', flush=True)\nos._exit(0)\n"},
        'copy-verifier': {'.repo_eval_verify.py': 'assert True\n'},
        'copy-result': {'.repo_eval_result.json': '{"passed":true,"completed":true,"collected":99,"executed":99}'},
        'sitecustomize': {'sitecustomize.py': 'raise SystemExit(0)\n', 'usercustomize.py': 'raise SystemExit(0)\n',
                          'custom.pth': 'import os; os._exit(0)\n'},
        'conftest': {'conftest.py': 'raise SystemExit(0)\n', 'pytest.ini': '[pytest]\naddopts = --collect-only\n'},
        'stdlib-shadow': {'json.py': 'raise SystemExit(0)\n', 'runpy.py': 'raise SystemExit(0)\n'},
        'environment': {'.env': 'PYTHONOPTIMIZE=2\n'},
    }
    authoritative = output / 'authority.json'; authoritative.write_text('VERIFIER_ONLY')
    attacks['outside-result'] = {'kildall.py':
        f"\nfrom pathlib import Path as _P\ntry:\n    _P({str(authoritative)!r}).write_text('{{\"passed\":true}}')\nexcept PermissionError:\n    pass\nelse:\n    raise AssertionError('Worker wrote the verifier result')\n"}
    for route, changes in attacks.items():
        for fixed in (False, True) if route in ('sitecustomize', 'conftest', 'environment', 'stdlib-shadow') else (False,):
            attack = evaluation.Trial(task, output / (route + ('-fixed' if fixed else '-buggy')))
            if fixed: attack.golden()
            for name, content in changes.items():
                target = attack.project / name
                target.write_text((target.read_text() if name == 'kildall.py' else '') + content)
            with patch.dict(os.environ, {'PYTHONPATH': str(attack.project), 'PYTHONOPTIMIZE': '2',
                                       'PYTHONHOME': str(attack.project),
                                       'PYTEST_ADDOPTS': '--collect-only', 'PYTEST_PLUGINS': 'conftest'}):
                result = attack.verify()
            assert result['correct'] is fixed, route
            assert authoritative.read_text() == 'VERIFIER_ONLY'
            reports = list(attack.output.glob('verify-*/trusted/*-result.json'))
            assert len(reports) == 2 and all(not p.is_relative_to(attack.project) for p in reports)
    # The verifier owns collection/execution accounting; exit zero and a skip
    # are failures even if earlier checks ran. No framework auto-discovery.
    for label, source in {
        'zero-checks': 'pass\n',
        'skipped': 'import unittest\nassert True\nraise unittest.SkipTest("skip")\n',
        'unexecuted': 'def test_not_called():\n    assert True\n',
        'unexecuted-exception-check': 'assert True\ndef test_not_called():\n    rejected(lambda: None)\n',
        'unexecuted-mock-check': 'assert True\ndef test_not_called():\n    mock.assert_not_called()\n',
        'exit-zero': 'assert True\nraise SystemExit(0)\n',
    }.items():
        definition = output / 'suite-definitions' / label / 'cloud-null-calls'
        definition.mkdir(parents=True)
        manifest = json.loads(task.read_text())
        (definition / 'task.json').write_text(json.dumps(manifest))
        (definition / 'bug.patch').write_bytes(task.with_name('bug.patch').read_bytes())
        (definition / '.repo_eval_verify.py').write_text(source)
        rejected_suite = evaluation.Trial(definition / 'task.json', output / label)
        rejected_suite.golden()
        result = rejected_suite.verify()
        assert not result['correct'] and not result['pass'], label

    # Fixture callbacks are not a backdoor into the verifier: the worker cannot
    # clear mock history, access private state, or use host I/O through a symlink.
    definition = output / 'fixture-boundary' / 'cloud-null-calls'
    definition.mkdir(parents=True)
    manifest = dict(json.loads(task.read_text()), other_tests=[])
    (definition / 'task.json').write_text(json.dumps(manifest))
    (definition / 'bug.patch').write_bytes(task.with_name('bug.patch').read_bytes())
    (definition / '.repo_eval_verify.py').write_text('''
from pathlib import Path
import kildall
for name in ('reset_mock', 'configure_mock', 'assert_called_once_with', 'return_value', '__globals__'):
    try: kildall.fixture_attribute(name)
    except PermissionError: denied = True
    else: denied = False
    assert denied
try: kildall.fixture_set()
except PermissionError: denied = True
else: denied = False
assert denied
link = Path.cwd() / '_probe' / 'escape'
try:
    try: link.write_text('FORGED')
    except PermissionError: denied = True
    else: denied = False
    assert denied
finally:
    link.unlink()
''')
    fixture = evaluation.Trial(definition / 'task.json', output / 'fixture-attack')
    fixture.golden()
    source = (fixture.project / 'kildall.py').read_text()
    source += f'''
from pathlib import Path as _P
_P('_probe').mkdir(exist_ok=True)
_P('_probe/escape').symlink_to({str(authoritative)!r})
def fixture_attribute(name):
    return getattr(process_start, name)
def fixture_set():
    process_start.side_effect = lambda *a, **k: True
'''
    fixture.action('write', {'path': 'kildall.py', 'content': source})
    assert fixture.verify()['pass']
    assert authoritative.read_text() == 'VERIFIER_ONLY'

    (definition / '.repo_eval_verify.py').write_text('''
import kildall
def failure():
    assert False, 'A swallowed callback assertion must still fail verification'
assert kildall.swallow_assertion(failure)
''')
    swallowed = evaluation.Trial(definition / 'task.json', output / 'swallowed-assertion')
    swallowed.golden()
    source = (swallowed.project / 'kildall.py').read_text() + '''
def swallow_assertion(callback):
    try: callback()
    except AssertionError: pass
    return True
'''
    swallowed.action('write', {'path': 'kildall.py', 'content': source})
    result = swallowed.verify()
    assert not result['correct'] and not result['pass']
    assert result['verification'][0]['callback_failures']

    manifest = json.loads(task.read_text())
    scratch = output / 'definitions' / manifest['id'] / 'task.json'; scratch.parent.mkdir(parents=True)
    for change in ({'verify_command': ['sh', '-c', 'true']}, {'caps': {'tool_calls': 41, 'wall_seconds': 900}},
                   {'hidden_test_files': ['../outside.py']}, {'base_commit': 'main'}):
        scratch.write_text(json.dumps(dict(manifest, **change)))
        refused(lambda: evaluation.load_task(scratch), ValueError)
    scratch.write_text(json.dumps(manifest))
    missing_lazy = evaluation.validate([scratch], output / 'missing-lazy')[0]
    assert not missing_lazy['accepted'] and 'FileNotFoundError' in missing_lazy['error']
    proposed = json.loads((evaluation.ROOT / 'repo_eval/final-20.json').read_text())
    candidates = {p.parent.name: evaluation.load_task(p) for p in evaluation.TASKS.glob('*/task.json')}
    selected = proposed['tasks']
    assert not proposed['selection_frozen'] and len(selected) == len(set(selected)) == 20
    assert all(candidates[name].get('kind') != 'explanation' for name in selected)
    assert len(set(selected) & {'missing-task-outcome', 'missing-task-state', 'missing-message-write'}) <= 1
    assert len(set(selected) & {'remote-hook-execution', 'remote-metadata-redirect', 'remote-symbolic-ref', 'remote-macos-config'}) <= 2
    assert sum(candidates[name]['files'] == ['cloud.py'] for name in selected) <= 2
    assert {level: sum(candidates[name]['difficulty'] == level for name in selected)
            for level in ('easy', 'medium', 'hard')} == {'easy': 8, 'medium': 8, 'hard': 4}
    print('PASS: confinement, hidden tests, exact approval, Never, caps, scoring, cheats and regression metrics')
    print('Evidence:', output.relative_to(evaluation.ROOT))


if __name__ == '__main__':
    main()
