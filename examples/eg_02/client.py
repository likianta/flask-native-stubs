from flask_native_stubs import setup_client
from flask_native_stubs.request import session

setup_client('127.0.0.1', 8081)
resp = session.post('hello-world', {
    'a': 123, 'b': True, 'c': 'hello from client!'
})

print(resp)
