from requests import Session as _Session


class Session:
    
    def __init__(self, serialization='json', exception_handle=0):
        self.host = None
        self.port = None
        self.protocol = 'http'
        self._exception_handle = exception_handle
        self._serialize: ...
        self._session = _Session()
        
        if serialization == 'json':
            from json import dumps, loads
        elif serialization == 'pickle':
            from pickle import dumps, loads
        else:
            raise Exception(f'Unknown serialization: {serialization}')
        self._serialize = dumps
        self._deserialize = loads
    
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
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
    
    def get(self, path: str, params: dict = None, _p=2):
        if self.host is None:
            print('[flask_native_stubs] You forgot calling '
                  '`flask_native_stubs.setup(...)` at the startup!', ':v4p')
            raise SystemExit(1)
        
        url = f'{self.url}/{path}'
        
        if params is None:
            resp = self._session.get(url)
        else:
            resp = self._session.get(
                url, params={'data': self._serialize(params)}
            )
        
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
            return self._deserialize(data)
        elif content_type == CONTENT_TYPE.ERROR:
            error_info = self._deserialize(data)
            if self._exception_handle <= 1:
                print(f'[RemoteError] {error_info["error"]}', f':v4p{_p}')
                exit(1)
            else:
                from textwrap import dedent
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
    
    @property
    def url(self) -> str:
        # assert self.host is not None
        return f'{self.protocol}://{self.host}:{self.port}'


class CONTENT_TYPE:  # noqa
    BASIC = 'application/python-basic'
    ERROR = 'application/python-error'
    OBJECT = 'application/python-object'
    TEXT = 'text/html'


session = Session()
