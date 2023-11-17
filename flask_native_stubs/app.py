from __future__ import annotations

import typing as t
from functools import partial
from functools import wraps

from flask import Flask

from .config import cfg
from .delegator import T as T0
from .delegator import delegate_native_call
from .delegator import delegate_remote_call
from .stubgen import update_runtime_info

__all__ = ['app', 'auto_route']


class T(T0):
    pass


class FlaskNative(Flask):
    collected_paths: set
    is_running: bool
    
    def __init__(self, name='flask_native_stubs'):
        self.collected_paths = set()
        self.is_running = False
        super().__init__(name)
    
    @staticmethod
    def auto_route(path=None) -> t.Union[T.NativeFunc, T.RemoteFunc]:
        return auto_route(path)
    
    def add_url_rule(
        self,
        rule: str,
        endpoint: str = None,
        view_func: t.Optional[t.Callable] = None,
        provide_automatic_options: t.Optional[bool] = None,
        **options: t.Any,
    ) -> None:
        super().add_url_rule(
            rule, endpoint, view_func,
            provide_automatic_options, **options
        )
        self.collected_paths.add(rule)
    
    def run(
        self,
        host: t.Optional[str] = None,
        port: t.Optional[int] = None,
        debug: t.Optional[bool] = None,
        load_dotenv: bool = True,
        **options: t.Any,
    ) -> None:
        cfg.running_mode = 'server'
        self.is_running = True
        super().run(host, port, debug, load_dotenv, **options)
        self.is_running = False
        cfg.running_mode = 'client'
    
    @staticmethod
    def shutdown(reason='') -> None:
        """
        note: currently i don't find a proper way to force stop flask progress.
        though i have checked [this answer <https://stackoverflow.com/questions
        /15562446/how-to-stop-flask-application-without-using-ctrl-c>]. so this
        method remains 'doing nothing'.
        """
        if reason: print(reason)
    
    @staticmethod
    def generate_stubs(dir_i: str, dir_o: str,
                       custom_map: dict[str, str] = None,
                       custom_filter: t.Sequence[str] = None) -> None:
        from .stubgen import generate_stubs
        generate_stubs(dir_i, dir_o, custom_map, custom_filter)


app = FlaskNative()


def auto_route(path: str = None) -> t.Union[T.NativeFunc, T.RemoteFunc]:
    """
    note: param `path` must start with '/'.
    """
    assert path is None or path.startswith('/')
    
    def decorator(func: T.NativeFunc) -> T.NativeFunc:
        nonlocal path
        if path is None:
            path = '/' + func.__name__.replace('_', '-')
        
        # stubgen recording
        update_runtime_info(func)
        
        if path in app.collected_paths:
            raise Exception(f'path ("{path}") already registered!')
        
        app.add_url_rule(
            path, func.__name__,
            partial(delegate_native_call(func), _is_native_call=False),
            methods=('POST', 'GET')
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> t.Any:
            if cfg.running_mode == 'server':
                return func(*args, **kwargs)
            else:
                return delegate_remote_call(path.lstrip('/'))(*args, **kwargs)
        
        return wrapper
    
    return decorator
