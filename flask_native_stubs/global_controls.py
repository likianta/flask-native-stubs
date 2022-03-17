COLLECT_RUNTIME_INFO = False

SERIALIZATION = 'json'

SIMULATION_MODE = False
''' do not edit this value manually. this is an "alias" to
    COLLECT_RUNTIME_INFO. '''

TRACEBACK_DETAILED_EXCEPTIONS = False
''' whether to expose server side tracebacks exceptions to client side.
    if True, client side will simulate server's traceback error.
    if False, client side raise a simple error info with no tarceback info.
    this is an experimental feature for debug only!
'''
