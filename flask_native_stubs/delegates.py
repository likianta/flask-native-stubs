import json
import pickle
import sys
from functools import wraps
from textwrap import dedent
from traceback import format_exc

import urllib3
from flask import Response
from flask import request
from requests import Session as _Session

from . import global_controls as gc
from .general import get_function_info


class Session:
    
    def __init__(self):
        self.host = None
        self.port = None
        self.protocol = 'http'
        self._session = _Session()
    
    def add_cert(self, cert_file: str, disable_warnings=True):
        """
        disable_warnings:
            if you're using a self-signed certificate, `requests` may raise
            `SubjectAltNameWarning`. we can disable this by setting
            `urllib3.disable_warnings`.
            
            https://stackoverflow.com/questions/42839363/python-disable-warnings
                -for-securitywarning-certificate-has-no-subjectaltnam
        """
        self.protocol = 'https'
        self._session.verify = cert_file
        if disable_warnings:
            urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
    
    def get(self, path: str, params: dict = None):
        return self._session.get(f'{self.url}/{path}', params=params)
    
    @property
    def url(self) -> str:
        # assert self.host is not None
        return f'{self.protocol}://{self.host}:{self.port}'


session = Session()


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
                # info['has_*args'], info['has_**kwargs']
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
            # see also `func delegate_call : (code occurrence) resp = get(...)`.
            return func(*params['args'], **params['kwargs'])
    
    return delegate


def delegate_return(func):
    @wraps(func)
    def delegate(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            if gc.TRACEBACK_DETAILED_EXCEPTIONS:
                error_msg = format_exc()
            else:
                error_msg = str(e)
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
        if session.host is None:
            print('[flask_native_stubs] You forgot calling '
                  '`flask_native_stubs.setup(...)` at the startup!', ':v4')
            raise SystemExit(1)
        
        if gc.SERIALIZATION == 'json':
            resp = session.get(path, params={'data': json.dumps({
                'args': args, 'kwargs': kwargs
            })})
        elif gc.SERIALIZATION == 'pickle':
            resp = session.get(path, params={'data': pickle.dumps({
                'args': args, 'kwargs': kwargs
            })})
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
            error_info = json.loads(data)
            if gc.TRACEBACK_DETAILED_EXCEPTIONS:
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
                print(f'[RemoteError] {error_info["error"]}', ':v4p2')
                sys.exit(1)
        else:
            raise Exception('Invalid content type: ' + content_type,
                            f'{session.url}/{path}')
    
    return delegate
