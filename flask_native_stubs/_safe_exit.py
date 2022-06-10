from .app import auto_route

error = None


@auto_route('--tell-server-im-done')
def client_is_done():
    from sys import exit
    from traceback import print_exception
    print_exception(error)
    exit(-1)
