COLLECT_RUNTIME_INFO = False

SERIALIZATION = 'json'

SIMULATION_MODE = False
''' do not edit this value manually. this is an "alias" to
    `COLLECT_RUNTIME_INFO`. '''

TRACEBACK_DETAILED_EXCEPTIONS = False
''' whether to expose server side tracebacks exceptions to client side.
    if True, client side raises a similar exception like server's tracebacks.
    if False, client side raises a similar exception but with no tarceback.
    this is an experimental feature for debug only!
'''
