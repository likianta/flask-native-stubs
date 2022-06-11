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
            # see also:
            #   [this file : def delegate_remote_call]
            #   [./request.py : class Session : def post : how it handles
            #       MimeType.ERROR and MimeType.CRITICAL_ERROR]
            return Response(func(*args, **kwargs))
            #   ps: if you are a daemon role. the `func` is actually a function
            #       in [this file : def delegate_remote_call]. so you can dive
            #       into [def delegate_remote_call : def delegate :
            #       session.post] to see what error may it happen.
        except Exception as e:
            if isinstance(e, WeakError):
                # respond and continue
                return Response(e)
            elif _is_expected_error():
                return Response(WeakError(e))
            else:
                # respond and exit
                #   note: the exit mechanism refers to [~/docs/way-to-exit-after
                #   -sending-response.zh.mo]
                # see also [./safe_exit.py] for traceback print_exception.
                return Response(CriticalError(e))
        except SystemExit as e2:
            from .protocol import ExitCode
            if e2.code == ExitCode.WEAK_ERROR:
                return Response(WeakError(
                    'The error is transmitted from server to client by daemon.'
                    #   server: where i receive this error.
                    #   client: where i'm going to transmit this error to.
                    #   daemon: i am the daemon.
                ))
            elif e2.code == ExitCode.CRITICAL_ERROR:
                return Response(CriticalError(
                    'The error is transmitted from server to client by daemon.'
                ))
            else:
                exit(e2.code)
    
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
