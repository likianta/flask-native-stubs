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
    TEXT = 'application/python-text'


class Response(_Response):
    def __init__(self, rv: t.Union[t.Any, WeakError, CriticalError]):
        if isinstance(rv, str):
            resp = rv
            type_ = MimeType.TEXT
        elif (isinstance(rv, (bool, int, bytes, float))
              or str(rv) in ('None', '()', '[]', '{}')):
            resp = str(rv)
            type_ = MimeType.PRIMITIVE
        elif isinstance(rv, WeakError):
            resp = str(rv)
            type_ = MimeType.ERROR
        elif isinstance(rv, CriticalError):
            from uuid import uuid1
            from . import _safe_exit
            _safe_exit.error_info = (rv.error, (code := str(uuid1())))
            resp = serializer.dumps({
                'info': str(rv.error),
                'code': code
            })
            type_ = MimeType.CRITICAL_ERROR
        else:
            resp = serializer.dumps(rv)
            type_ = MimeType.OBJECT
        super().__init__(resp, mimetype=type_)
