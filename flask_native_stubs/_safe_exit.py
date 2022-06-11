from typing import Literal

from .app import app
from .app import auto_route
from .protocol import CriticalError
from .protocol import ExitCode
from .protocol import WeakError

__all__ = ['error']

error = None


# DELETE: not used any more.
def on_error(func, args=(), kwargs=None, scheme: Literal[
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
def _client_is_done():
    from sys import exit
    from traceback import print_exception
    print_exception(error)
    exit(ExitCode.SAFE_EXIT)
