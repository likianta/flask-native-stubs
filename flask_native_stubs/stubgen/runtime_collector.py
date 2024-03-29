from __future__ import annotations

import typing as t
from collections import defaultdict

from .func_parser import T as T0
from .func_parser import parse_function
from .general import normpath


class T:
    _FilePath = str
    _FuncName = str
    RuntimeInfo = t.Dict[_FilePath, t.Dict[_FuncName, T0.FuncInfo]]


runtime_info: T.RuntimeInfo = defaultdict(dict)


def update_runtime_info(func) -> None:
    path = normpath(func.__code__.co_filename)
    info = parse_function(func)
    name = info['name']
    runtime_info[path][name] = info
    #   FIXME: this doesn't support custom url path for now.
