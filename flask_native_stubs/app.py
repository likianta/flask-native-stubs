from __future__ import annotations

import typing as t
from functools import partial

from flask import Flask

from .delegator import delegate_local_call

__all__ = ['app', 'auto_route']


class FlaskNative(Flask):
    collected_paths: set
    is_running = False
    
    def __init__(self, name='flask_native_stubs'):
        super().__init__(name)
        self.collected_paths = set()
    
    @staticmethod
    def auto_route(path=None) -> t.Callable:
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
        self.is_running = True
        super().run(host, port, debug, load_dotenv, **options)
        self.is_running = False
    
    @staticmethod
    def shutdown(reason=''):
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
                       custom_filter: t.Sequence[str] = None):
        from .stubgen import generate_stubs
        generate_stubs(dir_i, dir_o, custom_map, custom_filter)


# app = Flask('flask_native_stubs')
app = FlaskNative()


def auto_route(path: str = None) -> t.Callable:
    """
    note: param `path` must start with '/'.
    """
    assert path is None or path.startswith('/')
    
    def decorator(func):
        nonlocal path
        if path is None:
            path = '/' + func.__name__.replace('_', '-')
        
        # stubgen recording
        from .stubgen import update_runtime_info
        update_runtime_info(func)
        
        if path in app.collected_paths:
            raise Exception(f'path ("{path}") already registered!')
        
        app.add_url_rule(
            path, func.__name__,
            partial(delegate_local_call(func), _is_native_call=False),
            methods=('POST',)
        )
        
        return func
    
    return decorator
