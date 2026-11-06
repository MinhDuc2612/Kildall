"""Host interfaces. Only the existing Darwin implementations are available."""
from importlib import import_module
import sys


class UnsupportedPlatform(NotImplementedError):
    pass


def require(feature):
    if sys.platform != 'darwin':
        raise UnsupportedPlatform(f'{feature} not implemented on {sys.platform}')


def keys():
    require('Secure key store')
    return import_module('.darwin_keys', __name__)


def jobs():
    require('Scheduled jobs')
    return import_module('.darwin_jobs', __name__)


def ocr():
    require('Image OCR')
    return import_module('.darwin_ocr', __name__)


def system():
    require('Host runtime, sandbox and probes')
    return import_module('.darwin_system', __name__)


COMPUTER_REASON = 'Computer input and screen capture are unavailable until Phase 4C'


def refuse_computer(prefix):
    require('Computer mode')
    raise PermissionError(prefix + COMPUTER_REASON)
