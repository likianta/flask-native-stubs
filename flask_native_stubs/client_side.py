from functools import wraps
from inspect import currentframe

from .delegates import CONNECTION
from .delegates import delegate_call


def setup(host: str, port: int):
    CONNECTION.HOST = host
    CONNECTION.PORT = port


def add_route(func, path: str = None):
    delegate = _add_route(func, path)
    last_frame = currentframe().f_back
    last_frame.f_globals[func.__name__] = delegate


def _add_route(func, path: str = None):
    if path is None:
        path = func.__name__.replace('_', '-')
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        param_count = func.__code__.co_argcount
        param_names = func.__code__.co_varnames[:param_count]
        return delegate_call(path, param_names)(*args, **kwargs)
    
    return wrapper
