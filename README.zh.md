# Flask Native Stubs | Flask 原函数调用

像调用普通函数一样调用被 flask 装饰过的函数.

基本工作流程:

1. 创建 flask 的服务器端, 注意用 `@auto_route(...)` 替代 `@app.route(...)` 装饰路由;
2. 创建一个临时脚本, 用来生成 stub 文件;
3. 将生成的 stub 文件 (它们是 '.py' 后缀的脚本文件) 复制到客户端;
4. 客户端导入 stub 模块, 像调用普通函数一样使用它们.

下面的示例将帮助你掌握它:

用于演示的项目结构:

```
demo
|= server
   |- main.py
|= client
   |- main.py
```

1.  `server/main.py` 源代码如下:

    ```python
    from flask_native_stubs import app, auto_route

    @auto_route()
    def hello(a: int, b: str, c: float) -> list:
        # 函数的类型注解是可选的, 但是推荐您这么做!
        return [a, b, c]

    if __name__ == '__main__':
        app.run('localhost', 5000)
    ```

2.  创建一个临时脚本, 来生成 stub 文件:

    在 server 同目录下新建一个 'temp_stubgen.py':

    ```python
    import os
    from flask_native_stubs import enable_stubgen
    from flask_native_stubs import generate_stub_files

    enable_stubgen(project_root_path=os.getcwd())
    #   将只搜索 '~/server' 目录下的路由装饰函数.

    # 在此处, 显式地导入涉及路由装饰的函数所在的模块.
    from main import hello
    ...

    os.mkdir(d := 'server_stubs')
    generate_stub_files(dir_o=d)
    ```

    1.  运行临时脚本.
    2.  它会生成 'server/server_stubs' 文件夹 (里面包含有一个同名的 'main.py' 文件).

        该文件就是 'stub' 文件, 它同样也是 py 类型的文件.

        文件内容大致如下 (仅供参考):

        ```python
        """
        Auto-generated stub file by [flask-native-stubs][1].

        [1]: https://github.com/likianta/flask-native-stubs
        """
        from flask_native_stubs import add_route
        from typing import Any

        def hello(a: int, b: str, c: float) -> list: ...

        [add_route(x) for x in (hello,)]
        ```

3.  将 stub 文件复制到客户端.

    现在目录结构当如下所示:

    ```
    demo
    |= server
       |- main.py
       |- temp_stubgen.py
       |= server_stubs  # 1. 复制这个
           |- main.py
    |= client
       |- main.py
       |= server_stubs  # 2. 复制到这里
           |- main.py
    ```

4.  然后, 您可以借助这些 stub 文件编写客户端代码!

    'client/main.py':

    ```python
    from flask_native_stubs import setup
    from . import server_stubs as stubs

    setup(host='localhost', port=5000)
    #   注意: 你需要找服务器端的管理员要 host 和 port.

    def main():
        result = stubs.hello(a=123, b='456', c=7.89)
        #   ide 的静态分析和代码补全工作良好!
        print(result)  # -> [123, '456', 7.89]

    ...

    if __name__ == '__main__':
        main()
    ```

## 工作原理

本项目受启发于 swagger codegen.

*TODO*

## 注意事项

- 被路由装饰的函数不能包含 `*args` 和 `**kwargs`:

    ```python
    # don't
    @auto_route()
    def xxx(a, b, c, *args, d=1, e=None, **kwargs):
        ...
    ```
