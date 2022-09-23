if True:
    import sys
    import lk_logger
    from lk_utils import relpath
    sys.path.insert(0, relpath('..'))
    lk_logger.setup(quiet=True, show_varnames=True)

from argsense import cli
...


@cli.cmd()
def generate_stubs():
    pass


@cli.cmd()
def run_server():
    server.app.run('127.0.0.1', 5001)  # noqa


@cli.cmd()
def test_client():
    client.main()  # noqa


if __name__ == '__main__':
    cli.run()
