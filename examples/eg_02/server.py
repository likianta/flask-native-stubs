from flask_native_stubs import app, auto_route


@auto_route()
def hello_world(a: int, b: bool, c: str) -> str:
    print('received from client side:', a, b, c)
    return 'hello from server side!'


app.run(host='127.0.0.1', port=8081)
