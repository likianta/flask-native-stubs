import os
from functools import partial

from flask import Flask

from . import config
from .delegator import delegate_local_call
from .general import get_function_info

__all__ = ['app', 'auto_route']

app = Flask('flask_native_stubs')


# decorator way to add route
def auto_route(path=None):
    # note: param `path` should not add leading '/'.
    def decorator(func):
        nonlocal path
        if path is None:
            path = func.__name__.replace('_', '-')
        
        if config.SIMULATION_MODE:
            # for safety consideration, `app.add_url_rule` won't work in
            # simulation mode.
            pass
        else:
            app.add_url_rule(
                '/' + path, func.__name__,
                partial(delegate_local_call(func), _is_local_call=False),
                methods=('POST',)
            )
        
        if config.COLLECT_RUNTIME_INFO:
            from .stubgen import runtime_info_collection
            file_path = os.path.abspath(func.__code__.co_filename)
            # print(file_path, runtime_info_collection['root_path'])
            if file_path.startswith(runtime_info_collection['root_path']):
                info = get_function_info(func)
                # print(info)
                func_name = info.pop('name')
                runtime_info_collection['files'][file_path][func_name] = info
        
        return func
    
    return decorator
