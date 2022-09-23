from flask_native_stubs import setup_client

setup_client('127.0.0.1', 5001)


def main():
    from simple_02.client.stubs import server  # noqa
    response = server.hello(100, 'bbb', 2.0, True)
    print(response)
