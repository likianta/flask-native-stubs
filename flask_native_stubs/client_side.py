from functools import wraps
from inspect import currentframe

from .delegates import delegate_call
from .delegates import session


def setup(host: str, port: int, protocol='http', cert_file: str = ''):
    session.host = host
    session.port = port
    session.protocol = protocol
    if cert_file:
        # warning: if cer_file is given, the protocol will be forcely changed
        #   to 'https'.
        session.add_cert(cert_file)


def add_route(func, path: str = None):
    delegate = _add_route(func, path)
    last_frame = currentframe().f_back
    last_frame.f_globals[func.__name__] = delegate


def _add_route(func, path: str = None):
    if path is None:
        path = func.__name__.replace('_', '-')
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        return delegate_call(path)(*args, **kwargs)
    
    return wrapper
