# Flask Native Stubs

[中文版](https://blog.csdn.net/Likianta/article/details/125252446)

Call flask decorated functions like native ones.

Overall workflow:

1. Create server side functions, replace decorators from `@app.route(...)` to `@auto_route(...)`;
2. Create a temp script to generate server stub file;
3. Copy generated stub (folder) to client side;
4. Client imports stub files and use them like native functions.

Example for guide through:

```
demo
|= server
   |- main.py
|= client
   |- main.py
```

1.  `server/main.py` source code:

    ```python
    from flask_native_stubs import app, auto_route

    @auto_route()
    def hello(a: int, b: str, c: float) -> list:
        # type annotations are optional, but recommended.
        return [a, b, c]

    if __name__ == '__main__':
        app.run('localhost', 5000)
    ```

2.  Create a temp script like this:

    In 'server/temp_stubgen.py':

    ```python
    import os
    from flask_native_stubs import enable_stubgen
    from flask_native_stubs import generate_stub_files

    enable_stubgen(project_root_path=os.getcwd())
    #   will search `@auto_route` decorators only under '~/server'.

    # explicit import modules which contains routed functions.
    from main import hello
    ...

    os.mkdir(d := 'server_stubs')
    generate_stub_files(dir_o=d)
    ```

    1.  Run this script.
    2.  It will generate 'server/server_stubs' folder (contains a stub file named 'main.py').

        The stub file looks like:

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

3.  Copy the generated stub to client side:

    Now the directories are:

    ```
    demo
    |= server
       |- main.py
       |- temp_stubgen.py
       |= server_stubs  # 1. copy from
           |- main.py
    |= client
       |- main.py
       |= server_stubs  # 2. copy to
           |- main.py
    ```

4.  Write your client side implementations with server stubs:

    'client/main.py':

    ```python
    from flask_native_stubs import setup
    from . import server_stubs as stubs

    setup(host='localhost', port=5000)
    #   note: you should ask server admin to get the host and port.

    def main():
        result = stubs.hello(a=123, b='456', c=7.89)
        #   the ide works well with type hints :)
        print(result)  # -> [123, '456', 7.89]

    ...

    if __name__ == '__main__':
        main()
    ```

## How it works

This project is inspired by swagger codegen.

I want to get both type hints support and the convenience of native functions calling style. So let the mechanism become truth by some delegate hooks underlay.

Here are a few comparisons between swagger and flask-native-stubs:

- Workflow:
    - Swagger:
        1. Draw a blueprint by configuration files;
        2. Generate template code;
        3. Override templates to implement server and client logics.
    - Flask-native-stubs:
        1. We have implemented a flask app;
        2. Now generate stub files;
        3. Let the client side interact with stubs.
- *TODO:More...*

*TODO:ExplainFlaskNativeStubsImplementations*

## Cautions

- Do not use `*args` and `**kwargs` in decorated functions:

    ```python
    # don't
    @auto_route()
    def xxx(a, b, c, *args, d=1, e=None, **kwargs):
        ...
    ```
