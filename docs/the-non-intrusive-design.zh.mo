# 我们是如何实现 "非侵入式" 的设计的

flask-native-stubs 的 "非侵入式" 设计在于, 被添加了装饰器的函数, 不会改变原有的输入和输出预期.

请看下面的例子:

``` :codeblock(py)

from flask_native_stubs import auto_route

@auto_route()
def add(a: int, b: int, c: int) -> int:
    return a + b + c

if __name__ == '__main__':
    print(add(1, 2, 3))

```

原因是, 在装饰器内部, 会判断调用者来自远端还是本地.

如果来自本地, 则使用原始的 [`func(*args, **kwargs)`] 来处理; 否则, 才会使用 flask-native-stubs 特色封装来处理.

这里额外说明一下 flask-native-stubs 的 "特色" 封装工艺.

## flask-native-stubs "特色" 封装工艺

[#blue 当原函数出现非预期的报错时], flask-native-stubs (后面简称 "stubs") 会捕获该错误, 并把它封装为 [`NativeError(e)`] 实例.

[`NativeError(e)`] 实例通过 flask 的 Response 格式返回给远端的请求者.

请求者 (注: 请求者同样也使用了 flask-native-stubs 库) 判断类型为 [`NativeError`], 将它转换为一个可读的字符串格式, 并打印出来.

打印后, stubs 随即调用 [`sys.exit(-1)`] 和平退出. [/ exit 不是必须触发的. 请求者可以传一个 [`ignore_error=True`] 来忽略错误.]

[#blue 当原函数出现预期的报错时] (该报错由原函数内部的 raise 语句主动提出), stubs 的处理方式与上面相同, 只是在打印的内容上稍微有一点变化.

[#blue 当原函数正常执行并返回结果后], stubs 会把结果封装为 [`NativeResult(result)`] 实例, 并返回给请求者.
