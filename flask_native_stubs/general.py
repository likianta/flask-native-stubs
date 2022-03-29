def get_function_info(func) -> dict:
    """
    return:
        {
            'name': str func_name,
            'args': ((str arg_name, str arg_type), ...),
                                    ^ [1]
            'kwargs': ((str arg_name, str arg_type, any value), ...),
            'has_*args': bool,  # [3]
            'has_**kwargs': bool,  # [4]
            'return': str return_type,
                      ^ [2]
        }
        
        [1]: there is no empty type.
             for a callback case, it uses 'str';
             for an unknown type, it uses 'Any'.
        [2]: there is no empty return type.
             for a callback case, it uses 'None';
             for an unknown type, it uses 'Any'.
        [3][4]: v0.2 doesn't support.
    
    relevant:
        ./stubgen/runtime_stubgen.py
    """
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
        None : 'None',
        bool : 'bool',
        bytes: 'bytes',
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
        args.append(
            (name, type_2_str.get(annotations.get(name, str), 'Any'))
        )
    
    kwargs = []
    if kw_defaults:
        if isinstance(kw_defaults, tuple):
            kw_defaults = dict(
                zip(param_names[-len(kw_defaults):], kw_defaults)
            )
        for name, value in kw_defaults.items():
            kwargs.append(
                (name, type_2_str.get(annotations.get(name, str), 'Any'), value)
            )
    
    return_ = type_2_str.get(annotations.get('return', None), 'Any')
    
    return {
        'name'  : func_name,
        'args'  : args,
        'kwargs': kwargs,
        # 'has_*args'  : False,
        # 'has_**kwargs': False,
        'return': return_,
    }
