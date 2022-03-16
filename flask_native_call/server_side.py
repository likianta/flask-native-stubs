from functools import wraps
from inspect import currentframe

from flask import Flask

from .delegates import delegate_call
from .delegates import delegate_params
from .delegates import delegate_return

app = Flask('flask_native_stubs')


def add_route(func, path: str = None):
    delegate = _add_route(func, path)
    last_frame = currentframe().f_back
    last_frame.f_globals[func.__name__] = delegate


def auto_route(path=None):
    def decorator(func):
        return _add_route(func, path)
    
    return decorator


def _add_route(func, path: str = None):
    if path is None:
        path = func.__name__.replace('_', '-')
    
    delegate_func = delegate_params(func)
    delegate_func = delegate_return(delegate_func)
    app.add_url_rule('/' + path, None, delegate_func)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        param_count = func.__code__.co_argcount
        param_names = func.__code__.co_varnames[:param_count]
        return delegate_call(path, param_names)(*args, **kwargs)
    
    return wrapper
