import typing as t

from .app import app
from .app import auto_route
from .protocol import CriticalError
from .protocol import ExitCode
from .protocol import WeakError

__all__ = ['error_info']

# see only usage in [./response.py : def __init__]
error_info = None  # type: t.Optional[t.Tuple[Exception, str]]


# DELETE: not used any more.
def on_error(func, args=(), kwargs=None, scheme: t.Literal[
    'auto', 'exit', 'ignore', 'transmit',
] = 'auto'):
    try:
        return func(*args, **(kwargs or {}))
    # except Exception as e:
    #     pass
    except SystemExit as e:
        # exit code: 1 means WeakError, 2 means StrongError
        if scheme == 'auto':
            if app.is_running:
                if e.code == 1:
                    raise WeakError(e)
                else:
                    raise CriticalError(e)
            else:
                exit(e.code)
        elif scheme == 'exit':
            exit(e.code)
        elif scheme == 'ignore':
            return None
        elif scheme == 'transmit':
            assert app.is_running
            raise WeakError(e)
        else:
            raise ValueError(scheme)


@auto_route('--tell-server-im-done')
def _client_is_done(token: str):
    global error_info
    if not error_info:
        raise WeakError('The error stack is not setup.')
    error, code = error_info
    # print(':v', error, code, token, code == token)
    if token == code:
        from sys import exit
        if isinstance(error, Exception):
            from traceback import print_exception
            print_exception(error)  # noqa
        else:
            print(':v4', error or '')
        exit(ExitCode.SAFE_EXIT)
    else:
        raise WeakError(f'Invalid token: {token}')
