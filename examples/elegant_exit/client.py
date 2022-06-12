from flask_native_stubs.api import client_side

client_side.setup('127.0.0.1', 8081)
client_side.session.post('hello-world', {
    'a': 12,
    'b': 'bbb',
    'c': -1
})
