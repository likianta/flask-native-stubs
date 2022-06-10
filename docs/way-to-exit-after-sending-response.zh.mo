# 如何在 "sending response" 之后退出 flask 程序

假设场景中有一个 server 和一个 client. 二者都安装了 flask-native-stubs, 并通过 flask-native-stubs 提供的方法通讯.

+ server: 我的原函数遇到了一个致命的错误 (unexpected exception), 我不得不停止运行整个程序!
+ client: 等等, 在你停止之前, 你应该把我要的信息发给我.
+ server: 我遇到的错误导致我无法正确处理你的请求. 但我可以明确地把 "我发生了错误" 这件事如实告诉你.

    ``` :codeblock(py, title=server_side)

    from flask import Response
    ...

    class MyResponse(Response):

        def __init__(self, result):
            if isinstance(result, CriticalError):
                from . import _cache
                _cache.error = result.error
                #   我把这个错误暂存了起来.
                # 忍痛给你发了一个回复.
                super().__init__(
                    result.message,
                    mimetype='application/python-error'
                )
            ...

    ```

+ client: 我知道了. 既然你没办法处理. 我这边也没法继续我的事情, 所有我 (先你一步) 安全地退出了.

    ``` :codeblock(py, title=client_side)

    from flash_native_stubs import CriticalError
    ...

    def do_something(...):
        response = request_something(...)
        if isinstance(response, CriticalError):
            print('A critical error happened in remote server '
                  'with exit code ' + str(response.exit_code))
            tell_server_im_done()
            sys.exit(response.exit_code)

    ```

+ server: 好, 你已经退出了, 我这边也退出了.

    ``` :codeblock(py, title=server_side)

    from flask_native_stubs import auto_route
    ...

    @auto_route('/tell-server-im-done')
    def client_is_done():
        # 从暂存区取回错误, 并引爆它
        from ._cache import error
        if error:
            trace_print(error)
            sys.exit(-1)

    ```

# 关联代码

+ [flask_native_stubs/_safe_exit.py]
+ [flask_native_stubs/delegator.py : def delegate_local_call]
+ [flask_native_stubs/response.py : class Response : def __init__]
+ [flask_native_stubs/request.py : class Session : def post]

# 参考

- https://stackoverflow.com/questions/48994440/execute-a-function-after-flask-returns-response
