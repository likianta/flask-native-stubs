from random import randint

from flask_native_stubs import app


@app.auto_route()
def hello(name: str) -> int:
    print(f'hello {name}')
    return randint(0, 100)


if __name__ == '__main__':
    app.run('localhost', 2000)
