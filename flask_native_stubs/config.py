from os import getenv
from typing import Literal


class T:
    RunningMode = Literal['server', 'client']
    Serialization = Literal['json', 'pickle']


# noinspection PyTypeChecker
RUNNING_MODE: T.RunningMode = getenv('FLASK_NATIVE_RUNNING_MODE', 'server')
SERIALIZATION: T.Serialization = 'json'

if RUNNING_MODE == 'client':
    print('change running mode to "client" by environmental setting', ':pv2s')
    from random import randint
    from .request import setup_client
    setup_client(
        host=getenv('FLASK_NATIVE_HOST', 'localhost'),
        port=int(getenv('FLASK_NATIVE_PORT', randint(5000, 65535)))
    )
