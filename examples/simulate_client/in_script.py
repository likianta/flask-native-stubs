from random import randint

import lk_logger
from argsense import cli

from flask_native_stubs import app

lk_logger.setup(quiet=True, show_varnames=True)


@cli.cmd()
def main(mode: str) -> None:
    if mode == 'server':
        app.run('localhost', 2000)
    else:
        app.simulate_client('localhost', 2000)
        print(hello('world'))


@app.auto_route()
def hello(name: str) -> int:
    print(f'hello {name}')
    return randint(0, 100)


if __name__ == '__main__':
    # proc1: py examples/simulate_client/in_script.py server
    # proc2: py examples/simulate_client/in_script.py client
    cli.run(main)
