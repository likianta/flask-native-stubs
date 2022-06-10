import typing as t
from functools import wraps

from flask import request

from .protocol import CriticalError
from .protocol import WeakError
from .protocol import serializer
from .response import Response


def delegate_local_call(func: t.Callable):
    @wraps(func)
    def delegate(*args, _is_local_call=True, **kwargs):
        if _is_local_call:
            return func(*args, **kwargs)
        
        # adapt params
        assert args == () and kwargs == {}  # note: use `==`, not `is`.
        # ref: https://blog.csdn.net/qq_44862918/article/details/91041637
        if post_data := request.get_data():
            params = serializer.loads(post_data)
            args, kwargs = params['args'], params['kwargs']
        
        try:
            return Response(func(*args, **kwargs))
        except Exception as e:
            if isinstance(e, WeakError):
                # respond and continue
                return Response(e)
            elif _is_expected_error():
                return Response(WeakError(e))
            else:
                # respond and exit
                #   note: the exit mechanism refers to [<~/docs/way-to-exit
                #   -after-sending-response.zh.mo>]
                # see also [./_safe_exit.py] for traceback print_exception.
                return Response(CriticalError(e))
    
    return delegate


def _is_expected_error() -> bool:
    # https://stackoverflow.com/questions/48448414/display-source-code-causing
    # -an-exception-in-python
    from inspect import trace
    # print(':vl', list(enumerate(trace()[1])))
    return bool(trace()[1][4][0].lstrip().startswith('raise '))


def delegate_remote_call(path: str):
    from .request import session
    
    def delegate(*args, **kwargs):
        return session.post(path, {
            'args': args, 'kwargs': kwargs,
        })
    
    return delegate
