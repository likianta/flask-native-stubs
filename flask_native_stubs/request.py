import typing as t

from requests import Session as _Session

from .protocol import serializer
from .response import MimeType

__all__ = ['session', 'setup']


class Session:
    
    def __init__(self, exception_handle=0):
        self.host = None
        self.port = None
        self.protocol = 'http'
        self._exception_handle = exception_handle
        self._serialize: ...
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
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)
    
    def post(self, path: str, params: dict = None) -> t.Any:
        url = f'{self.url}/{path}'
        resp = self._session.post(
            url, params and {'data': serializer.dumps(params)}
        )
        data = resp.content  # type: bytes
        content_type = resp.headers['Content-Type'].split(';')[0]
        #   `~.split(';')[0]`: e.g. 'text/html; charset=utf-8' -> 'text/html'
        
        if resp.status_code >= 400:
            raise Exception(f'HTTP status code error: {resp.status_code}', data)
        
        if content_type == MimeType.TEXT:
            return data.decode('utf-8').strip()
        elif content_type == MimeType.PRIMITIVE:
            return eval(data)
        elif content_type == MimeType.OBJECT:
            return serializer.loads(data)
        elif content_type == MimeType.ERROR:
            print(data)
            exit(1)
        elif content_type == MimeType.CRITICAL_ERROR:
            print(data)
            self.post('/--tell-server-im-done')
            exit(1)
        else:
            raise Exception('Unknown content type: ' + content_type, url)
    
    @property
    def url(self) -> str:
        if self.host is None:
            print('[flask_native_stubs] You forgot calling '
                  '`flask_native_stubs.setup(...)` at the startup!', ':v4p2')
            exit(1)
        return f'{self.protocol}://{self.host}:{self.port}'


session = Session()


def setup(host: str, port: int, protocol='http', cert_file: str = ''):
    global session
    session.host = host
    session.port = port
    session.protocol = protocol
    if cert_file:
        # warning: if cer_file is given, the protocol will be forcely changed
        #   to 'https'.
        session.add_cert(cert_file)
