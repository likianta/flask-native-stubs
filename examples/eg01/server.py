import lk_logger
lk_logger.setup(quiet=True, show_varnames=True)

from flask_native_stubs import app
from flask_native_stubs import config

config.STUBGEN_MODE = True


@app.auto_route()
def hello(a: int, b: str, c: float, d: bool = None) -> list:
    print(a, b, c, d)
    return [a, b, c, d]


app.generate_stubs(
    '.', './lib',
    {
        'server.py': 'server_stub.py',
    },
    (
        './lib',
    )
)
# app.run('127.0.0.1', 5001)
