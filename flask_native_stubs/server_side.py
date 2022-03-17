import os.path

from flask import Flask

from . import global_controls as gc
from .delegates import delegate_params
from .delegates import delegate_return
from .general import get_function_info
from .stubgen import runtime_info_collection

app = Flask('flask_native_stubs')


def auto_route(path=None):
    def decorator(func):
        nonlocal path
        if path is None:
            path = func.__name__.replace('_', '-')
        
        delegate_func = delegate_params(func)
        delegate_func = delegate_return(delegate_func)
        app.add_url_rule('/' + path, None, delegate_func)
        
        if gc.COLLECT_RUNTIME_INFO:
            file_path = os.path.normpath(func.__code__.co_filename)
            # print(file_path, runtime_info_collection['root_path'])
            if file_path.startswith(runtime_info_collection['root_path']):
                info = get_function_info(func)
                # print(info)
                func_name = info.pop('name')
                runtime_info_collection['files'][file_path][func_name] = info
        
        return func
    
    return decorator
