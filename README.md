# Flask Native Stubs

[中文版](https://blog.csdn.net/Likianta/article/details/125252446)

Call flask decorated functions like native ones.

Overall workflow:

1. Create server side functions, use `@app.auto_route(...)` instead of `@app.route(...)`.
2. In server side, finally call `app.generate_stubs(...)` instead of `app.run(...)`. -- This creates a "stubs" folder that contains all magic routes.
3. Copy generated stubs (folder) to client side.
4. Client imports stub files and use them like native functions.

## Installation

```
pip install flask-native-stubs
```

The latest version is 0.4.2+.

## Quick Start

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
    from flask_native_stubs import app

    @app.auto_route()
    def hello(a: int, b: str, c: float) -> list:
        # type annotations are optional, but recommended.
        return [a, b, c]

    if __name__ == '__main__':
        app.generate_stubs(
            dir_i='.',
            dir_o='./stubs',
        )
        # app.run('localhost', 5000)
    ```

2.  Run `server/main.py` and get "stubs" folder like below:

    ```
    demo
    |= server
       |= stubs  # <- generated stubs
          |- __init__.py
          |- main.py  # <- a `hello` function is defined in it.
       |- main.py
    |= client
       |- main.py
    ```

2.  Move "stubs" folder to client side:

    ```
    demo
    |= server
       |- main.py
    |= client
       |= stubs
          |- __init__.py
          |- main.py  # <- a `hello` function is defined in it.
       |- main.py
    ```

3.  Write your client side code:

    'client/main.py':

    ```python
    from flask_native_stubs import setup_client
    from .stubs import main as server_stubs

    # note: you may ask the server admin to get the ip address.
    setup_client('localhost', 5000)

    def main():
        response = server_stubs.hello(a=123, b='456', c=7.89)
        #   the IDE works well with type hints.
        print(response)  # -> [123, '456', 7.89]

    if __name__ == '__main__':
        main()
    ```

## How it works

This project is inspired by swagger codegen.

I want to get both typing annotations support and the convenience of native functions calling style. So let the mechanism works by some delegate hooks underlay.

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
    @app.auto_route()
    def xxx(a, b, c, *args, d=1, e=None, **kwargs):
        ...
    ```
