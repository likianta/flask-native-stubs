if True:
    import sys
    import lk_logger
    from lk_utils import relpath
    sys.path.insert(0, relpath('..'))
    lk_logger.setup(quiet=True, show_varnames=True)

from argsense import cli
from simple_02.server import main as server
from simple_02.client import main as client


@cli.cmd()
def generate_stubs():
    server.app.generate_stubs(
        dir_i=(i := relpath('./server')),
        dir_o=(o := relpath('./server/stubs')),
        custom_map={
            f'{i}/main.py': f'{o}/server.py'
        }
    )

    # -------------------------------------------------------------------------
    # move from ~/server/stubs to ~/client/stubs
    import os
    import shutil
    
    dir_i = relpath('./server/stubs')
    dir_o = relpath('./client/stubs')
    
    if os.path.exists(dir_o):
        shutil.rmtree(dir_o)
    shutil.move(dir_i, dir_o)
    print(f'see result in ~/client/stubs')


@cli.cmd()
def run_server():
    server.app.run('127.0.0.1', 5001)


@cli.cmd()
def test_client():
    client.main()


if __name__ == '__main__':
    cli.run()
