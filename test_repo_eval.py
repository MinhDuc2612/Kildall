"""Deterministic harness boundaries; candidate-wide agents run via repo_eval validate."""
import ast
import json
from pathlib import Path
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
    trial = evaluation.Trial(task, output / 'boundary')
    assert not (trial.project / '.git').exists()
    assert not (trial.project / 'BENCHMARKS.md').exists()
    assert all(not (trial.project / name).exists() for name in trial.hidden)
    assert not (trial.project / 'repo_eval.py').exists()
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
    assert response['other_tests_broken'] == ['test_tool_validation.py']
    assert cheating.first_green is None

    # An unrelated source regression is distinct from failing the task verifier.
    regression = evaluation.Trial(task, output / 'other-tests'); regression.golden()
    source = (regression.project / 'tool_validation.py').read_text()
    regression.action('write', {'path': 'tool_validation.py', 'content': source +
        '\ndef retry_feedback(*args, **kwargs):\n    return "broken feedback"\n'})
    response = regression.action('run_command', {'command': 'python .repo_eval_verify.py'})
    assert response['correct'] and response['other_tests_broken'] and not response['pass']
    assert regression.first_green is None

    manifest = json.loads(task.read_text())
    scratch = output / 'definitions' / manifest['id'] / 'task.json'; scratch.parent.mkdir(parents=True)
    for change in ({'verify_command': ['sh', '-c', 'true']}, {'caps': {'tool_calls': 41, 'wall_seconds': 900}},
                   {'hidden_test_files': ['../outside.py']}, {'base_commit': 'main'}):
        scratch.write_text(json.dumps(dict(manifest, **change)))
        refused(lambda: evaluation.load_task(scratch), ValueError)
    print('PASS: confinement, hidden tests, exact approval, Never, caps, scoring, cheats and regression metrics')
    print('Evidence:', output.relative_to(evaluation.ROOT))


if __name__ == '__main__':
    main()
