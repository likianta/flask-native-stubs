from typing import Literal


class T:
    Protocol = Literal['http', 'https', 'websocket']
    RunningMode = Literal['client', 'server']
    Serialization = Literal['json', 'pickle']


class _Config:
    protocol: T.Protocol = 'http'  # TODO
    running_mode: T.RunningMode = 'client'
    serialization: T.Serialization = 'json'
    
    host: str
    port: int


cfg = _Config()


def setup(
    host: str,
    port: int,
    protocol: T.Protocol = None,
    cert_file: str = None
) -> None:
    from .request import session
    
    cfg.host = host
    cfg.port = port
    
    session.host = host
    session.port = port
    
    if cert_file and protocol and protocol != 'https':
        print(
            'warn: if cert_file is given, the protocol will be '
            'forcely set to "https"'
        )
        protocol = 'https'
    if protocol:
        session.protocol = protocol
    if cert_file:
        session.add_cert(cert_file)
