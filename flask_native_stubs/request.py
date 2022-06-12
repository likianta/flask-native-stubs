import typing as t

from requests import Session as _Session

from .protocol import ExitCode
from .protocol import WeakError
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
            from urllib3.exceptions import SubjectAltNameWarning
            urllib3.disable_warnings(SubjectAltNameWarning)
    
    def post(self, path: str, params: dict = None) -> t.Any:
        url = f'{self.url}/{path}'
        resp = self._session.post(url, params and serializer.dumps(params))
        data = resp.content  # type: bytes
        content_type = resp.headers['Content-Type'].split(';')[0]
        #   `~.split(';')[0]`: e.g. 'text/html; charset=utf-8' -> 'text/html'
        
        if resp.status_code >= 400:
            print(':v4p4', f'HTTP status code error: {resp.status_code}', data)
            #     ~~~~^^~
            ''' print(':p?', ...): this is featured by [lib:lk-logger].
                here is a simple illustration:
                    p0: self (current frame)
                    p1: ./delegator.py : def delegate_remote_call
                    p2: ./stubgen/add_route.py : def _add_route
                    p3: ./stubgen/add_route.py : def add_route
                    p4: real caller
            '''
            exit(1)
        
        if content_type == MimeType.TEXT:
            return data.decode('utf-8').strip()
        elif content_type == MimeType.PRIMITIVE:
            return eval(data)
        elif content_type == MimeType.OBJECT:
            return serializer.loads(data)
        elif content_type == MimeType.ERROR:
            text = data.decode(encoding='utf-8')
            print('[RemoteError]', text, ':v4p4')
            exit(ExitCode.WEAK_ERROR)
            #   see also its catcher at [./delegator.py : def delegate_local
            #   _call : def delegate : try catch function error : SystemExit]
        elif content_type == MimeType.CRITICAL_ERROR:
            info = serializer.loads(data)
            print('[RemoteError]', info['info'], ':v5p4')
            try:
                self._session.post(
                    f'{self.url}/--tell-server-im-done',
                    {'token': info['code']}
                )
            except:
                pass
            finally:
                exit(ExitCode.CRITICAL_ERROR)
                #   see also its catcher at [./delegator.py : def delegate_local
                #   _call : def delegate : try catch function error :
                #   SystemExit]
        else:
            raise Exception('Unknown content type: ' + content_type, url)
    
    @property
    def url(self) -> str:
        if self.host is None:
            print('[flask_native_stubs] You forgot calling '
                  '`flask_native_stubs.setup(...)` at the startup!', ':v4p5')
            exit(1)
        return f'{self.protocol}://{self.host}:{self.port}'
    
    @staticmethod  # DELETE: not used any more.
    def _exit(info, force: bool = False) -> t.Optional[WeakError]:
        from .app import app
        if force:
            exit(1)
        if app.is_running:
            """ a daemon role for example.
                client - daemon - server
                         ~~~~~~ i'm daemon
                    1. server responds a WeakError to daemon
                    2. daemon deliveries the same error to client
                    3. client exits. (daemon and server are still running)
            """
            return WeakError(info)
        else:
            """ else a client role.
                client - daemon - server
                ~~~~~~ i'm client
            """
            exit(1)


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
