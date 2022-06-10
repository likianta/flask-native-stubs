import typing as t
from functools import wraps

from flask import request

from .protocol import CriticalError
from .protocol import WeakError
from .protocol import serializer


def delegate_local_call(func: t.Callable):
    @wraps(func)
    def delegate(*args, _is_local_call=True, **kwargs):
        if not _is_local_call:
            return func(*args, **kwargs)
        
        # adapt params
        assert args == () and kwargs == {}  # note: use `==`, not `is`.
        params = serializer.loads(request.args['data'])
        args, kwargs = params['args'], params['kwargs']
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, WeakError):
                # respond and continue
                return e
            else:
                # respond and exit
                #   note: the exit mechanism refers to [<~/docs/way-to-exit
                #   -after-sending-response.zh.mo>]
                return CriticalError(e)
    
    return delegate


def delegate_remote_call(path: str):
    from .request import session
    
    def delegate(*args, **kwargs):
        return session.post(path, {
            'args': args, 'kwargs': kwargs,
        })
    
    return delegate
