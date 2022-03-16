# Flask Native Stubs | Flask 原函数调用

像调用普通函数一样调用被 flask 装饰过的函数.

查看下面的实例:

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
    app.run('localhost', 8080)
```

client.py

```python
from server import hello_world
response = hello_world(123, '456', 7.89)
#   它相当于 requests.get('http://localhost:8080/hello-world', {...}) 的高级封装.
print(response)  # -> [123, '456', 7.89]
```

它展现了以下特点:

1. 自动解析被装饰的函数的参数类型 (根据 annotations 信息)
2. 代理发起请求
3. 代理返回结果
4. 调用者可以充分利用 IDE 的 "静态分析" 优势

## 实现原理

*TODO*

## 注意事项

1. 参数限制
    1. 必须对参数添加类型注解, 其中 str 类型可省略.
    2. 只接受基本类型: int, float, bool, str. 暂不支持可变类型, 例如 dict! (我将在下个版本加入支持所有可序列化的类型.)
    3. 暂不支持 `*args` 和 `**kwargs` 传参.
2. 返回值要求可被序列化.
3. server 代码随同 client 一起打包. 或者, server 应提供伪代码 (只保留函数名称, 接口和返回值类型) 随同打包.
