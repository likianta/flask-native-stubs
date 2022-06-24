from examples.eg01.lib import server_stub as stub
from flask_native_stubs import setup_client

setup_client('127.0.0.1', 5001)

response = stub.hello(100, 'bbb', 2.0, True)
print(response)
