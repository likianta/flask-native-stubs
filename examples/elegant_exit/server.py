from flask_native_stubs import CriticalError
from flask_native_stubs import WeakError
from flask_native_stubs import app

# be noticed: both CriticalError and WeakError will be translated to SystemExit
#   to client side.


@app.auto_route()
def make_an_error(severity: int) -> str:
    print(severity)
    if severity == 0:
        return 'no error happens'
    elif severity == 1:
        raise WeakError('there is a weak error')
    else:
        raise CriticalError('a critical error...')


if __name__ == '__main__':
    app.run('127.0.0.1', 5001)
