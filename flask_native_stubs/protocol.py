from __future__ import annotations

import typing as t

from .config import cfg

__all__ = ['ExitCode', 'CriticalError', 'WeakError', 'serializer']


class T:
    Error = t.Union[str, Exception, None]
    Serialization = t.Literal['json', 'pickle']


class Serializer:
    
    def __init__(self, serialization: T.Serialization):
        self.SERIALIZATION = serialization
        
        if serialization == 'json':
            import json
            self.loads = json.loads
            self.dumps = json.dumps
        else:
            import pickle
            self.loads = pickle.loads
            self.dumps = pickle.dumps


serializer = Serializer(cfg.serialization)


class WeakError(Exception):
    error: Exception = None
    position: tuple[str, int]  # file name and line number
    content: str  # error message
    
    def __init__(self, error: T.Error = None):
        # info = getframeinfo(currentframe().f_back)
        # self.position = (info.filename, info.lineno)
        self.content = str(error) if error else ''
        if isinstance(error, Exception):
            self.error = error
    
    def __str__(self):
        return self.content


class CriticalError(Exception):  # TODO: rename to 'StrongError'?
    """ the critical/fatal/unexpected error. """
    
    def __init__(self, error: T.Error = None):
        self.error = error


class ExitCode:
    # https://blog.csdn.net/wenyiCodeDog/article/details/99184206
    WEAK_ERROR = 10
    CRITICAL_ERROR = 12
    SAFE_EXIT = 0
