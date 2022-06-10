from __future__ import annotations

import typing as t
from inspect import currentframe  # noqa
from inspect import getframeinfo  # noqa

from . import config

__all__ = ['CriticalError', 'WeakError', 'serializer']


class Serializer:
    
    def __init__(self, serialization: t.Literal['json', 'pickle']):
        self.SERIALIZATION = serialization
        
        if serialization == 'json':
            import json
            self.loads = json.loads
            self.dumps = json.dumps
        else:
            import pickle
            self.loads = pickle.loads
            self.dumps = pickle.dumps


serializer = Serializer(config.SERIALIZATION)


class WeakError(Exception):
    position: tuple[str, int]  # file name and line number
    content: str  # error message
    
    def __init__(self, error=None):
        # info = getframeinfo(currentframe().f_back)
        # self.position = (info.filename, info.lineno)
        self.content = str(error) if error else ''
    
    def __str__(self):
        return self.content


class CriticalError(Exception):
    
    def __init__(self, error):
        self.error = error
