import json
import pickle
from functools import wraps
from traceback import format_exc

from flask import Response
from flask import request

from . import config
from .general import get_function_info
from .requests import CONTENT_TYPE
from .requests import session


def delegate_params(func):
    info = get_function_info(func)
    
    @wraps(func)
    def delegate(*args, **kwargs):
        if not any((
                info['args'], info['kwargs'],
                # info['has_*args'], info['has_**kwargs']
        )):
            return func()
        
        if args or kwargs:
            return func(*args, **kwargs)
        
        else:
            # args is () and kwargs is {}, we should gain the real params from
            #   flask `request`.
            serialized_data: str = request.args['data']
            if config.SERIALIZATION == 'json':
                params = json.loads(serialized_data)
            elif config.SERIALIZATION == 'pickle':
                # FIXME: `pickle` is not safe.
                params = pickle.loads(serialized_data.encode('utf-8'))
            else:
                # TODO: custom deserializer, for example, encrypted data.
                raise Exception(f'Unknown deserializer: {config.SERIALIZATION}')
            # see also `func delegate_call : (code occurrence) resp = get(...)`.
            return func(*params['args'], **params['kwargs'])
    
    return delegate


def delegate_return(func):
    @wraps(func)
    def delegate(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            if config.EXCEPTION_HANDLE == 0:
                raise e
            elif config.EXCEPTION_HANDLE == 1:
                error_msg = str(e)
            else:
                error_msg = format_exc()
            result = json.dumps({
                'filename': func.__code__.co_filename,
                'lineno'  : func.__code__.co_firstlineno,
                'funcname': func.__name__,
                'error'   : error_msg,
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
                    }, ':v4')
                    raise e
                # # result = json.dumps(result, default=str)
                mimetype = CONTENT_TYPE.OBJECT
        return Response(result, mimetype=mimetype)
    
    return delegate


def delegate_call(path: str):
    def delegate(*args, **kwargs):
        return session.get(path, params={
            'args': args, 'kwargs': kwargs,
        })
    
    return delegate
