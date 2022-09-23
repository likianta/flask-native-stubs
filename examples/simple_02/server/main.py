from flask_native_stubs import app


@app.auto_route()
def hello(a: int, b: str, c: float, d: bool = None) -> list:
    print(a, b, c, d)
    return [a, b, c, d]


if __name__ == '__main__':
    app.run('127.0.0.1', 5001)
