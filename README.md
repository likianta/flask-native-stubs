# Flask Native Call

- [中文版](README.zh.md)

Call flask decorated functions like native ones.

Have a glance:

```
demo
|- server.py
|- client.py
```

server.py

```python
from flask_native_call import app, auto_route

@auto_route()
def hello_world(a: int, b: str, c: float) -> bool:
    print(a)
    print(b)
    print(c)
    return [a, b, c]

if __name__ == '__main__':
    app.run('localhost', 5000)
```

client.py

```python
from server import hello_world
from flask_native_call import setup
setup('localhost', 5000)  # match server address
response = hello_world(123, '456', 7.89)
#   internally, it works the same like:
#       `requests.get('localhost:8080/hello-world', {...})`
print(response)  # -> [123, '456', 7.89]
```

## How it works

1.  Server analyses decorated function:
    1.  Collect all parameters info (names, type annotations, etc.).
    2.  Register function name (kebab-case) to route map.
    3.  Delegate this function...

        If other function calls this, it internally emits a request to the running server;

        when server responsed, deserialize the response and return it to the caller.

## Cautions

*TODO*
