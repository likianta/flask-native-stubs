import typing as t

from flask import Response as _Response

from .protocol import CriticalError
from .protocol import WeakError
from .protocol import serializer

__all__ = ['MimeType', 'Response']


class MimeType:
    PRIMITIVE = 'application/python-primitive'
    OBJECT = 'application/python-object'
    ERROR = 'application/python-error'
    CRITICAL_ERROR = 'application/python-critical-error'
    TEXT = 'text/html'


class Response(_Response):
    def __init__(self, result: t.Union[t.Any, WeakError, CriticalError]):
        if isinstance(result, WeakError):
            resp = str(result)
            type_ = MimeType.ERROR
        elif isinstance(result, CriticalError):
            from . import _safe_exit
            _safe_exit.error = result.error
            resp = 'A critical error happened in remote server. ' \
                   '(The server is going to shut down.)'
            type_ = MimeType.CRITICAL_ERROR
        elif (isinstance(result, (bool, int, bytes, float, str))
              or str(result) in ('None', '()', '[]', '{}')):
            resp = str(result)
            type_ = MimeType.PRIMITIVE
        else:
            resp = serializer.dumps(result)
            type_ = MimeType.OBJECT
        super().__init__(resp, mimetype=type_)
