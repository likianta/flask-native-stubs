import json
import sys
from functools import wraps

from flask import Response
from flask import request
from requests import get

from . import intermediate


class ContentType:
    BASIC = 'application/python-basic'
    TEXT = 'text/html'
    OBJECT = 'application/python-object'
    ERROR = 'application/python-error'


def delegate_params(func):
    # warning:
    #   1. `func:params` mustn't include `*args` or `**kwargs`.
    #   2. if one from `func:params` is not str type, it must be explicitly
    #      annotated.
    #   3. this doesn't support complex types, it supports only:
    #      bool, float, int, str.
    #   4. if `func` has default args, the default args must be annotated
    #      correctly. for example:
    #           def some_func(a, b, c: bool = None):
    #               #               ^^^^^^^^^^^^^^
    #               #   param `c` must be annotated correctly (ps: if its type
    #               #   is str, you can leave it out), otherwise we will
    #               #   recognize it as str type.
    #               ...
    
    param_count = func.__code__.co_argcount
    param_names = func.__code__.co_varnames[:param_count]
    annotations = func.__annotations__
    del param_count
    
    # collect func's parameters.
    preset_params = {}  # dict[str param, str annotated_type]
    for param in param_names:
        preset_params[param] = annotations.get(param, str)
    del param_names
    del annotations
    
    def delegate(*args, **kwargs):
        if not preset_params:
            # assert not args and not kwargs
            return func()
        elif args or kwargs:
            return func(*args, **kwargs)
        else:
            real_args = {}
            for param, type_ in preset_params.items():
                if param in request.args:
                    if type_ is bool:
                        real_args[param] = bool(eval(request.args[param]))
                        #   FIXME: `eval` operation is dangerous!
                    else:
                        real_args[param] = type_(request.args[param])
            return func(**real_args)
    
    return delegate


def delegate_return(func):
    """
    notes:
        all exceptions are catched and wrapped with `Response`, they will not
        be raised in server side, but outburst in client side.
    """
    
    @wraps(func)
    def delegate(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception:
            from traceback import format_exc
            result = json.dumps({
                'filename'  : func.__code__.co_filename,
                'lineno'    : func.__code__.co_firstlineno,
                'funcname'  : func.__name__,
                'error_info': format_exc()
            })
            mimetype = ContentType.ERROR
        else:
            if isinstance(result, str):
                mimetype = ContentType.TEXT
            elif result is None or type(result) in (bool, int, float):
                result = str(result)
                mimetype = ContentType.BASIC
            else:
                try:
                    result = json.dumps(result)
                except Exception as e:
                    print('You are returning a non-serializable object!', {
                        'filename': func.__code__.co_filename,
                        'lineno'  : func.__code__.co_firstlineno,
                        'funcname': func.__name__,
                    })
                    raise e
                # # result = json.dumps(result, default=str)
                mimetype = ContentType.OBJECT
        return Response(result, mimetype=mimetype)
    
    return delegate


def delegate_call(path: str, arg_names: tuple):
    def delegate(*args, **kwargs):
        for name, arg in zip(arg_names, args):
            kwargs[name] = arg
        from lk_logger import lk
        lk.loga(kwargs)
        
        if intermediate.host is None:
            print('[flask_native_stubs] You forgot to call '
                  '`flask_native_stubs.setup(...)` at the startup!')
            sys.exit(1)
        else:
            url = f'http://{intermediate.host}:{intermediate.port}/{path}'
        
        resp = get(url, params=kwargs)  # FIXME
        data = resp.content  # type: bytes
        content_type = resp.headers['Content-Type'].split(';')[0]
        #   `~.split(';')[0]`: e.g. 'text/html; charset=utf-8' -> 'text/html'
        
        if resp.status_code >= 400:
            raise Exception(f'HTTP status code error: {resp.status_code}', data)
        
        if content_type == ContentType.TEXT:
            return data.decode('utf-8').strip()
        elif content_type == ContentType.BASIC:
            return eval(data)
        elif content_type == ContentType.OBJECT:
            return json.loads(data)
        elif content_type == ContentType.ERROR:
            from textwrap import dedent
            error_info = json.loads(data)
            raise Exception(dedent('''
                APXF Error:
                    Unexpected error happend at {}:{} >> {}
                    Error info: {}
            ''').format(
                error_info['filename'],
                error_info['lineno'],
                error_info['funcname'],
                error_info['error_info'],
            ).strip())
        else:
            raise ValueError('Invalid content type: ' + content_type, url)
    
    return delegate
