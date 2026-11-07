"""JSON object bridge. Candidate code runs only in the sandboxed worker process."""
import base64
import builtins
import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import select
import socket
import struct
import sys
import threading
import types

LIMIT = 2_000_000


def send(channel, message):
    data = json.dumps(message, allow_nan=False).encode()
    if len(data) > LIMIT:
        raise ValueError('Oversized worker message')
    channel.sendall(struct.pack('!I', len(data)) + data)


def receive(channel):
    def read(size):
        chunks = bytearray()
        while len(chunks) < size:
            block = channel.recv(size - len(chunks))
            if not block:
                raise EOFError('Worker closed its channel')
            chunks.extend(block)
        return bytes(chunks)
    size, = struct.unpack('!I', read(4))
    if size > LIMIT:
        raise ValueError('Oversized worker message')
    return json.loads(read(size))


class Remote:
    def __init__(self, bridge, ident):
        object.__setattr__(self, '_bridge', bridge)
        object.__setattr__(self, '_ident', ident)

    def operation(self, operation, *args, **kwargs):
        return self._bridge.call(operation, self._ident, args, kwargs)

    def __getattribute__(self, name):
        if name == '__new__': return object.__getattribute__(self, 'operation')('get', name)
        return object.__getattribute__(self, name)

    def __getattr__(self, name): return self.operation('get', name)
    def __setattr__(self, name, value): return self.operation('set', name, value)
    def __delattr__(self, name): return self.operation('delete', name)
    def __call__(self, *args, **kwargs): return self.operation('call', *args, **kwargs)
    def __getitem__(self, key): return self.operation('item', key)
    def __setitem__(self, key, value): return self.operation('put', key, value)
    def __iter__(self): return self.operation('iter')
    def __next__(self): return self.operation('next')
    def __len__(self): return self.operation('len')
    def __bool__(self): return self.operation('bool')
    def __enter__(self): return self.operation('enter')
    def __exit__(self, kind, value, tb):
        return self.operation('exit', kind, value, None)


class Bridge:
    def __init__(self, control, callbacks, *, worker=False):
        self.control, self.callbacks, self.worker = control, callbacks, worker
        self.objects, self.pending, self.exception_types = {}, {}, {}
        self.counter = 0
        self.callback_failures = []
        self.owner = threading.get_ident()
        self.callback_lock = threading.RLock()

    def encode(self, value):
        if type(value) in (str, int, float, bool, type(None)):
            return value
        if isinstance(value, Remote):
            return {'ref': value._ident, 'owner': 'host' if self.worker else 'worker'}
        if isinstance(value, Path): return {'path': str(value)}
        if type(value) is bytes: return {'bytes': base64.b64encode(value).decode()}
        if type(value) in (list, tuple, set, frozenset):
            return {'sequence': type(value).__name__, 'items': [self.encode(v) for v in value]}
        if type(value) is dict:
            return {'mapping': [[self.encode(k), self.encode(v)] for k, v in value.items()]}
        if type(value) is types.SimpleNamespace:
            return {'namespace': self.encode(vars(value))}
        if isinstance(value, type) and issubclass(value, BaseException):
            name = value.__module__ + '.' + value.__name__
            self.exception_types[name] = value
            return {'exception_type': name, 'bases': [c.__name__ for c in value.__mro__[1:]]}
        if isinstance(value, BaseException):
            return {'exception': self.encode(type(value)), 'args': self.encode(value.args)}
        ident = str(id(value))
        self.objects[ident] = value
        return {'ref': ident, 'owner': 'worker' if self.worker else 'host'}

    def decode(self, value):
        if not isinstance(value, dict): return value
        if 'ref' in value:
            if value['owner'] == ('worker' if self.worker else 'host'):
                return self.objects[value['ref']]
            return Remote(self, value['ref'])
        if 'path' in value: return Path(value['path'])
        if 'bytes' in value: return base64.b64decode(value['bytes'], validate=True)
        if 'mapping' in value: return {self.decode(k): self.decode(v) for k, v in value['mapping']}
        if 'sequence' in value:
            kind = {'list': list, 'tuple': tuple, 'set': set, 'frozenset': frozenset}[value['sequence']]
            return kind(self.decode(v) for v in value['items'])
        if 'namespace' in value: return types.SimpleNamespace(**self.decode(value['namespace']))
        if 'exception_type' in value:
            name = value['exception_type']
            if name not in self.exception_types:
                module, _, attribute = name.rpartition('.')
                base = next((getattr(builtins, n) for n in value['bases']
                             if isinstance(getattr(builtins, n, None), type)
                             and issubclass(getattr(builtins, n), BaseException)), Exception)
                known = getattr(builtins, name.removeprefix('builtins.'), None)
                if self.worker or module in ('subprocess', 'sqlite3', 'urllib.error', 'unittest.case'):
                    known = getattr(importlib.import_module(module), attribute, None)
                if known is not None and (not isinstance(known, type) or not issubclass(known, BaseException)):
                    raise ValueError('Worker supplied a non-exception type')
                self.exception_types[name] = known if known is not None else type(attribute, (base,), {'__module__': module})
            return self.exception_types[name]
        if 'exception' in value:
            return self.decode(value['exception'])(*self.decode(value['args']))
        raise ValueError('Malformed worker value')

    def dispatch(self, message, channel):
        ident = message['id']
        try:
            operation = message['operation']
            args, kwargs = self.decode(message['args']), self.decode(message['kwargs'])
            if self.worker and operation == 'import':
                result = importlib.import_module(*args)
            elif not self.worker and operation == 'output':
                if args[0] not in ('stdout', 'stderr'): raise ValueError('Unknown stream')
                result = getattr(sys, args[0]).write(args[1])
            else:
                target = self.objects[message['target']]
                # Host callbacks are explicit fixture capabilities, not an import or
                # introspection API into the verifier. Never expose frames/globals.
                if not self.worker:
                    from unittest.mock import Mock
                    if operation in ('set', 'delete', 'put'):
                        raise PermissionError('Verifier fixture state is read-only')
                    if operation in ('get', 'set', 'delete') and args[0].startswith('_'):
                        raise PermissionError('Private verifier attributes are unavailable')
                    if operation in ('get', 'set', 'delete') and isinstance(target, (types.FunctionType, types.MethodType)):
                        raise PermissionError('Fixture functions are callable only')
                    if operation == 'get' and isinstance(target, Mock):
                        if (args[0].startswith(('assert', 'mock', 'reset', 'configure', 'attach'))
                                or args[0] in ('return_value', 'side_effect', 'called', 'call_count', 'call_args', 'call_args_list')):
                            raise PermissionError('Verifier mock bookkeeping is unavailable')
                    if operation == 'get' and not isinstance(target, Mock):
                        allowed = set()
                        if isinstance(target, (io.StringIO, io.BytesIO)):
                            allowed |= {'read', 'readline', 'write', 'flush', 'close', 'getvalue', 'status', 'headers'}
                        if isinstance(target, threading.Event): allowed |= {'set', 'clear', 'wait', 'is_set'}
                        if type(target).__module__ == '__main__': allowed |= {'open', 'check'}
                        if args[0] not in allowed:
                            raise PermissionError('Verifier fixture attribute is unavailable')
                if operation == 'get': result = getattr(target, *args)
                elif operation == 'set': result = setattr(target, *args)
                elif operation == 'delete': result = delattr(target, *args)
                elif operation == 'call': result = target(*args, **kwargs)
                elif operation == 'item': result = target[args[0]]
                elif operation == 'put': target[args[0]] = args[1]; result = None
                elif operation == 'iter': result = iter(target)
                elif operation == 'next': result = next(target)
                elif operation == 'len': result = len(target)
                elif operation == 'bool': result = bool(target)
                elif operation == 'enter': result = target.__enter__()
                elif operation == 'exit': result = target.__exit__(*args)
                else: raise ValueError('Unknown worker operation')
            reply = {'reply': ident, 'value': self.encode(result)}
        except BaseException as error:
            if not self.worker and isinstance(error, AssertionError):
                self.callback_failures.append(str(error))
            reply = {'reply': ident, 'error': self.encode(error)}
        send(channel, reply)

    def call(self, operation, target=None, args=(), kwargs=None):
        channel = self.callbacks if self.worker else self.control
        lock = self.callback_lock if self.worker else contextlib.nullcontext()
        with lock:
            self.counter += 1
            ident = self.counter
            send(channel, {'id': ident, 'operation': operation, 'target': target,
                           'args': self.encode(args), 'kwargs': self.encode(kwargs or {})})
            while ident not in self.pending:
                readers = [channel]
                if not self.worker: readers.append(self.callbacks)
                elif threading.get_ident() == self.owner: readers.append(self.control)
                ready, _, _ = select.select(readers, [], [], 60)
                if not ready: raise TimeoutError('Worker protocol timed out')
                for source in ready:
                    message = receive(source)
                    if 'reply' in message: self.pending[message['reply']] = message
                    else: self.dispatch(message, source)
            reply = self.pending.pop(ident)
            if 'error' in reply: raise self.decode(reply['error'])
            return self.decode(reply['value'])

    def module(self, name): return self.call('import', args=(name,))


class Output:
    def __init__(self, bridge, name): self.bridge, self.name = bridge, name
    def write(self, value): return self.bridge.call('output', args=(self.name, value))
    def flush(self): pass
    def isatty(self): return False


if __name__ == '__main__':
    bridge = Bridge(socket.socket(fileno=int(sys.argv[1])), socket.socket(fileno=int(sys.argv[2])), worker=True)
    # -I -S excludes startup customization, cwd, PYTHONPATH and site packages.
    # Product modules are found only after all interpreter/stdlib paths.
    sys.path.extend(json.loads(sys.argv[3]))  # Fixed paths; never execute .pth files.
    sys.path.append(os.getcwd())
    sys.stdout, sys.stderr = Output(bridge, 'stdout'), Output(bridge, 'stderr')
    while True:
        try: bridge.dispatch(receive(bridge.control), bridge.control)
        except EOFError: break
