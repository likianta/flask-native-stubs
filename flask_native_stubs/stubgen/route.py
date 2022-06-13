"""
the black magic to make stubs work in client side like native functions.
warning: this is for internal use only.
"""
from inspect import currentframe
from typing import Callable


def magic_route(func, path: str = None):
    delegate = _add_route(func, path)
    last_frame = currentframe().f_back
    last_frame.f_globals[func.__name__] = delegate


def _add_route(func, path: str = None) -> Callable:
    from ..delegator import delegate_remote_call
    
    if path is None:
        path = func.__name__.replace('_', '-')
    
    return delegate_remote_call(path)
