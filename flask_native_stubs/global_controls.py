COLLECT_RUNTIME_INFO = False

SERIALIZATION = 'json'

THROW_EXCEPTIONS_TO_CLIENT_SIDE = False
''' if True, all exceptions will be catched and encapsulated to `Response`,
    they will not be raised in server side, but outburst in client side.
    this is an experimental feature for debug only!
'''