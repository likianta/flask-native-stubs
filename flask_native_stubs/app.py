from __future__ import annotations

import typing as t
from functools import partial

from flask import Flask

from . import config
from .delegator import delegate_local_call

__all__ = ['app', 'auto_route']


class FlaskNative(Flask):
    is_running = False
    
    def __init__(self, name='flask_native_stubs'):
        super().__init__(name)
    
    @staticmethod
    def auto_route(path=None) -> t.Callable:
        return auto_route(path)
    
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
                       filenames_map: dict[str, str] = None):
        from .stubgen import generate_stubs
        generate_stubs(dir_i, dir_o, filenames_map)


# app = Flask('flask_native_stubs')
app = FlaskNative()


def auto_route(path=None) -> t.Callable:
    # note: param `path` should not add leading '/'.
    def decorator(func):
        nonlocal path
        if path is None:
            path = func.__name__.replace('_', '-')
        
        if config.STUBGEN_MODE:
            from .stubgen import update_runtime_info
            update_runtime_info(func)
            # for safety consideration, `app.add_url_rule` won't work in
            # stubgen mode. (otherwise, it may cause a view function endpoint
            # overwriting error.)
        else:
            app.add_url_rule(
                '/' + path, func.__name__,
                partial(delegate_local_call(func), _is_local_call=False),
                methods=('POST',)
            )
        
        return func
    
    return decorator
