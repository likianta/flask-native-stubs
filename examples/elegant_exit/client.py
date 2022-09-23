from flask_native_stubs import setup_client

setup_client('127.0.0.1', 5001)


def main():
    """
    be noticed:
        if server raises a WeakError or a CriticalError, the client will
        receive a SystemExit exception.
    """
    from elegant_exit.stubs import server  # noqa
    try:
        rsp = server.make_an_error(severity=0)
        print(rsp)
    except Exception as e:
        print('severity = 0', e)
    try:
        rsp = server.make_an_error(severity=1)
        print(rsp)
    except (Exception, SystemExit) as e:
        print('severity = 1', e)
    try:
        rsp = server.make_an_error(severity=2)
        print(rsp)
    except (Exception, SystemExit) as e:
        print('severity = 2', e)
