import json
import pickle
import sys
from functools import wraps
from traceback import format_exc

from flask import Response
from flask import request
from requests import get

from . import global_controls as gc
from .general import get_function_info


class CONNECTION:
    HOST: str = None
    PORT: int = None


class CONTENT_TYPE:  # noqa
    BASIC = 'application/python-basic'
    ERROR = 'application/python-error'
    OBJECT = 'application/python-object'
    TEXT = 'text/html'


def delegate_params(func):
    info = get_function_info(func)
    
    @wraps(func)
    def delegate(*args, **kwargs):
        if not any((
                info['args'], info['kwargs'],
                info['has_*args'], info['has_**kwargs']
        )):
            return func()
        
        if args or kwargs:
            return func(*args, **kwargs)
        
        else:
            # args is () and kwargs is {}, we should gain the real params from
            #   flask `request`.
            serialized_data: str = request.args['data']
            if gc.SERIALIZATION == 'json':
                params = json.loads(serialized_data)
            elif gc.SERIALIZATION == 'pickle':
                # FIXME: `pickle` is not safe.
                params = pickle.loads(serialized_data.encode('utf-8'))
            else:
                # TODO: custom deserializer, for example, encrypted data.
                raise Exception(f'Unknown deserializer: {gc.SERIALIZATION}')
            return func(**params)
    
    return delegate


def delegate_return(func):
    @wraps(func)
    def delegate(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            if gc.THROW_EXCEPTIONS_TO_CLIENT_SIDE is False:
                # return Response(mimetype=CONTENT_TYPE.ERROR)
                raise e
            result = json.dumps({
                'filename': func.__code__.co_filename,
                'lineno'  : func.__code__.co_firstlineno,
                'funcname': func.__name__,
                'error'   : format_exc()
            })
            mimetype = CONTENT_TYPE.ERROR
        else:
            if isinstance(result, str):
                mimetype = CONTENT_TYPE.TEXT
            elif result is None or type(result) in (bool, int, float):
                result = str(result)
                mimetype = CONTENT_TYPE.BASIC
            else:
                try:
                    result = json.dumps(result)
                except Exception as e:
                    print('You cannot return un-serializable object!', {
                        'filename': func.__code__.co_filename,
                        'lineno'  : func.__code__.co_firstlineno,
                        'funcname': func.__name__,
                    })
                    raise e
                # # result = json.dumps(result, default=str)
                mimetype = CONTENT_TYPE.OBJECT
        return Response(result, mimetype=mimetype)
    
    return delegate


def delegate_call(path: str, arg_names: tuple):
    def delegate(*args, **kwargs):
        for name, arg in zip(arg_names, args):
            kwargs[name] = arg
        # print(kwargs)
        
        if CONNECTION.HOST is None:
            print('[flask_native_stubs] You forgot calling '
                  '`flask_native_stubs.setup(...)` at the startup!')
            sys.exit(1)
        else:
            url = f'http://{CONNECTION.HOST}:{CONNECTION.PORT}/{path}'
        
        if gc.SERIALIZATION == 'json':
            resp = get(url, params={'data': json.dumps(kwargs)})
        elif gc.SERIALIZATION == 'pickle':
            resp = get(url, params={'data': pickle.dumps(kwargs)})
        else:
            raise Exception(f'Unknown serializer: {gc.SERIALIZATION}')
        
        data = resp.content  # type: bytes
        content_type = resp.headers['Content-Type'].split(';')[0]
        #   `~.split(';')[0]`: e.g. 'text/html; charset=utf-8' -> 'text/html'
        
        if resp.status_code >= 400:
            raise Exception(f'HTTP status code error: {resp.status_code}', data)
        
        if content_type == CONTENT_TYPE.TEXT:
            return data.decode('utf-8').strip()
        elif content_type == CONTENT_TYPE.BASIC:
            return eval(data)
        elif content_type == CONTENT_TYPE.OBJECT:
            return json.loads(data)
        elif content_type == CONTENT_TYPE.ERROR:
            from textwrap import dedent
            error_info = json.loads(data)
            raise Exception(dedent('''
                Error occurred in the remote server:
                    Unexpected error happend at {}:{} >> {}
                    Error info: {}
            ''').format(
                error_info['filename'],
                error_info['lineno'],
                error_info['funcname'],
                error_info['error'],
            ).strip())
        else:
            raise Exception('Invalid content type: ' + content_type, url)
    
    return delegate
