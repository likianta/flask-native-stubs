"""
source: https://github.com/likianta/argsense-cli
    [lib:argsense/parser/func_parser.py]
"""
import typing as t

__all__ = ['parse_function', 'TFuncInfo']


class T:
    _ParamName = str
    ParamType = t.Literal[
        'any', 'bool', 'dict', 'float', 'int',
        'list', 'none', 'set', 'str', 'tuple',
    ]
    FallbackType = t.Literal['any', 'str']
    _DefaultValue = t.Any
    
    FuncInfo = t.TypedDict('FuncInfo', {
        'name'  : str,
        'args'  : t.List[t.Tuple[_ParamName, ParamType]],
        'kwargs': t.List[t.Tuple[_ParamName, ParamType, _DefaultValue]],
        'return': ParamType,  # noqa
    })


def parse_function(func, fallback_type: T.FallbackType = 'any') -> T.FuncInfo:
    param_count = func.__code__.co_argcount + func.__code__.co_kwonlyargcount
    param_names = func.__code__.co_varnames[:param_count]
    annotations = func.__annotations__
    kw_defaults = func.__defaults__ or ()
    # print(func.__name__, param_count, param_names, annotations, kw_defaults)
    
    func_name = func.__name__
    args: list
    kwargs: list
    return_: str
    
    type_2_str = {
        None : 'none',
        bool : 'bool',
        dict : 'dict',
        float: 'float',
        int  : 'int',
        list : 'list',
        set  : 'set',
        str  : 'str',
        tuple: 'tuple',
    }
    
    args = []
    if kw_defaults:
        arg_names = param_names[:-len(kw_defaults)]
    else:
        arg_names = param_names
    for name in arg_names:
        if name in annotations:
            type_ = annotations[name]
            type_str = type_2_str.get(type_, str(type_))
        else:
            type_str = fallback_type
        args.append((name, type_str))
    
    kwargs = []
    if kw_defaults:
        if isinstance(kw_defaults, tuple):
            kw_defaults = dict(
                zip(param_names[-len(kw_defaults):], kw_defaults)
            )
        for name, value in kw_defaults.items():
            if name in annotations:
                type_ = annotations[name]
                type_str = type_2_str.get(type_, str(type_))
            else:
                type_str = _deduce_param_type_by_default_value(value)
            kwargs.append((name, type_str, value))
    
    if 'return' in annotations:
        type_ = annotations['return']
        type_str = type_2_str.get(type_, str(type_))
        # print(type_, type_str, ':v')
    else:
        type_str = type_2_str[None]
    return_ = type_str
    
    return {
        'name'  : func_name,
        'args'  : args,
        'kwargs': kwargs,
        'return': return_,
    }


def _deduce_param_type_by_default_value(default: t.Any) -> T.ParamType:
    dict_ = {
        bool : 'bool',
        dict : 'dict',
        float: 'float',
        int  : 'int',
        list : 'list',
        set  : 'set',
        str  : 'str',
        tuple: 'tuple',
    }
    return dict_.get(type(default), 'any')


TFuncInfo = T.FuncInfo
