if True:
    import sys
    import lk_logger
    from lk_utils import relpath
    sys.path.insert(0, relpath('..'))
    lk_logger.setup(quiet=True, show_varnames=True)

from argsense import cli
from simple_01 import server, client


@cli.cmd()
def generate_stubs():
    server.app.generate_stubs(
        dir_i=relpath('.'),
        dir_o=relpath('./stubs'),
    )
    print(f'see result in ~/stubs')


@cli.cmd()
def run_server():
    server.app.run('127.0.0.1', 5001)


@cli.cmd()
def test_client():
    client.main()


if __name__ == '__main__':
    cli.run()
