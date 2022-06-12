import lk_logger

from flask_native_stubs import CriticalError
from flask_native_stubs import app
from flask_native_stubs import auto_route

lk_logger.setup(show_varnames=True)


@auto_route()
def hello_world(a, b, c: int):
    print(a, b, c)
    if c < 0:
        raise CriticalError('a critical error...')


app.run('127.0.0.1', 8081)
