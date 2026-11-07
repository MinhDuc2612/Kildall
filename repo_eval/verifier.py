"""Trusted assertions and result writer; never imports candidate Python files."""
import ast
import json
import os
from pathlib import Path
import socket
import sys
import threading
import traceback
import types
import unittest
from unittest.mock import patch as local_patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from worker import Bridge


class ProductModule(types.ModuleType):
    def __init__(self, name, bridge):
        super().__init__(name)
        self.__dict__['_bridge'] = bridge

    def __getattr__(self, name): return self._bridge.module(self.__name__).__getattr__(name)
    def __setattr__(self, name, value): self._bridge.module(self.__name__).__setattr__(name, value)
    def __delattr__(self, name): self._bridge.module(self.__name__).__delattr__(name)


class Checks(ast.NodeTransformer):
    def __init__(self): self.collected = []

    def visit_Assert(self, node):
        self.generic_visit(node)
        ident = len(self.collected)
        self.collected.append(node.lineno)
        call = ast.Call(func=ast.Name(id='_verifier_check', ctx=ast.Load()),
                        args=[ast.Constant(ident), node.test, node.msg or ast.Constant(None)], keywords=[])
        return ast.copy_location(ast.Expr(value=call), node)

    def visit_Call(self, node):
        self.generic_visit(node)
        name = node.func.id if isinstance(node.func, ast.Name) else getattr(node.func, 'attr', '')
        if name == 'rejected' or name.startswith('assert_'):
            ident = len(self.collected)
            self.collected.append(node.lineno)
            return ast.copy_location(ast.Call(func=ast.Name(id='_verifier_call', ctx=ast.Load()),
                args=[ast.Constant(ident), node.func, *node.args], keywords=node.keywords), node)
        return node


def run(config):
    control = socket.socket(fileno=config['control_fd'])
    callbacks = socket.socket(fileno=config['callbacks_fd'])
    bridge = Bridge(control, callbacks)
    installed = {}
    checks, executed, failed = Checks(), set(), []
    result = {'started': True, 'completed': False, 'collected': 0, 'executed': 0,
              'skipped': False, 'passed': False}
    try:
        source = Path(config['suite']).read_text()
        code = checks.visit(ast.parse(source, filename=config['suite']))
        result['collected'] = len(checks.collected)
        if not checks.collected:
            raise ValueError('Verifier suite collected zero checks')
        code = compile(ast.fix_missing_locations(code), config['suite'], 'exec', optimize=0)

        def check(ident, condition, message):
            executed.add(ident)
            if not condition:
                failed.append(ident)
                raise AssertionError(message)

        def checked_call(ident, function, *args, **kwargs):
            executed.add(ident)
            try:
                return function(*args, **kwargs)
            except AssertionError:
                failed.append(ident)
                raise

        # Candidate modules are RPC objects. Their globals cannot replace exec,
        # runpy, assertions, imports, environment, or this process's result writer.
        for name in config['modules']:
            if name in sys.modules:
                raise ValueError('Product name collides with trusted module: ' + name)
            installed[name] = ProductModule(name, bridge)
            sys.modules[name] = installed[name]
        kildall = installed['kildall']
        remote_thread = bridge.module('threading').Thread

        def patch_object(target, attribute, *args, **kwargs):
            if target is threading.Thread: target = remote_thread
            return local_patch.object(target, attribute, *args, **kwargs)

        def patch_target(target, *args, **kwargs):
            if target.startswith('builtins.'):
                return patch_object(bridge.module('builtins'), target.split('.', 1)[1], *args, **kwargs)
            return local_patch(target, *args, **kwargs)

        patch_target.object = patch_object
        # Only the trusted test's patch helper is adapted. Stdlib stays local;
        # product mocks are explicit, bounded capabilities supplied to the worker.
        class Imports:
            def __call__(self, name, globals=None, locals=None, fromlist=(), level=0):
                module = __import__(name, globals, locals, fromlist, level)
                if name == 'unittest.mock' and 'patch' in fromlist:
                    from types import SimpleNamespace
                    return SimpleNamespace(Mock=unittest.mock.Mock, patch=patch_target)
                return module

        import builtins
        namespace = dict(vars(builtins), __import__=Imports())
        with local_patch.object(kildall, 'process_start', return_value='verifier-owner'):
            exec(code, {'__name__': '__main__', '__file__': config['suite'],
                        '__builtins__': namespace, '_verifier_check': check, '_verifier_call': checked_call})
        if len(executed) != len(checks.collected):
            raise ValueError('Verifier suite left collected checks unexecuted')
        if failed or bridge.callback_failures:
            raise AssertionError('A verifier assertion failed in a product callback')
        result.update(completed=True, passed=True)
    except BaseException as error:
        result['skipped'] = isinstance(error, unittest.SkipTest)
        result['error'] = type(error).__name__ + ': ' + str(error)
        traceback.print_exc()
    finally:
        result['executed'] = len(executed)
        result['failed_checks'] = failed
        result['callback_failures'] = bridge.callback_failures
        result['missing'] = [line for ident, line in enumerate(checks.collected) if ident not in executed]
        control.close(); callbacks.close()
        for name in installed: sys.modules.pop(name, None)
    return result


if __name__ == '__main__':
    config = json.loads(Path(sys.argv[1]).read_text())
    # Only this process receives the private report FD. Both execution processes
    # are denied writes outside candidate home; the controller persists this
    # trusted report outside the copy. Worker stdout/exit/files never score.
    result = run(config)
    with os.fdopen(config['result_fd'], 'w') as stream:
        json.dump(result, stream, allow_nan=False)
