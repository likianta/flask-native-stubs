"""
collect runtime info, generate stub files.
usage: `~/docs/how-to-generate-python-stub-files-(pyi).zh.md`.
"""
import os
from collections import defaultdict
from textwrap import dedent

from .. import global_controls as gc

runtime_info_collection = {
    'root_path': '',
    'files'    : defaultdict(dict)
}
''' {
        'root_path': str,
        'files': {
            str filepath: {
                str func_name: {
                    # see `../general.py`
                    'args': ...,
                    'kwargs': ...,
                    'has_*args': ...,  # v0.1.0 doesn't support
                    'has_**kwargs': ...,  # v0.1.0 doesn't support
                    'return': ...,
                }, ...
            }, ...
        }
    }
'''


def generate_stub_files(dir_o: str, flat_dir=False) -> None:
    if gc.COLLECT_RUNTIME_INFO is False:
        raise Exception('Runtime info collection is not enabled! '
                        'Did you forget to call `flask_native_stubs'
                        '.enable_stubgen()`?')
    if not runtime_info_collection['files']:
        raise Exception('No decorated functions collected!')
    
    # print(runtime_info_collection)
    
    if flat_dir:
        os.makedirs(dir_o, exist_ok=True)
        all_file_paths = tuple(runtime_info_collection['files'])
        all_file_names = tuple(map(os.path.basename, all_file_paths))
        assert len(all_file_names) == len(set(all_file_names)), (
            'Cannot apply `flat_dir` feature: there are duplicate file names!'
        )
        io_map = {fp: f'{dir_o}/{fn}' for fp, fn in zip(
            all_file_paths, all_file_names
        )}
    else:
        io_map = _create_empty_dirs(dir_o, add_init_file=False)
    
    for file, v0 in runtime_info_collection['files'].items():
        file_i = file
        file_o = io_map[file_i]
        
        function_names = []
        function_defs = []
        for func_name, v1 in v0.items():
            function_names.append(func_name)
            function_defs.append('def {}({}) -> {}: ...'.format(
                func_name,
                ', '.join((
                    *(f'{x}: {y}' for x, y in v1['args']),
                    # *(('*args',) if v1['has_*args'] else ()),
                    *(f'{x}: {y} = {z}' for x, y, z in v1['kwargs']),
                    # *(('**kwargs',) if v1['has_**kwargs'] else ()),
                )),
                v1['return'],
            ))
        
        with open(file_o, 'w', encoding='utf-8') as f:
            f.write(dedent('''
                """
                Auto-generated stub file by [flask-native-stubs][1].
                
                [1]: https://github.com/likianta/flask-native-stubs
                """
                from flask_native_stubs import add_route
                from typing import Any
                
                {functions}
                
                [add_route(x) for x in ({function_names},)]
            ''').lstrip().format(
                functions='\n\n'.join(function_defs),
                function_names=', '.join(function_names),
            ))
        print(f'file generated: {file_o}')


def _create_empty_dirs(dir_o: str, add_init_file: bool) -> dict:
    root_dir_i = runtime_info_collection['root_path'].replace('\\', '/')
    root_dir_o = dir_o.replace('\\', '/')
    
    dirs_i = set(
        os.path.dirname(x)
        for x in runtime_info_collection['files']
    )
    common_prefix_i = os.path.commonpath(tuple(dirs_i)).rstrip('/')
    assert common_prefix_i.startswith(root_dir_i)
    
    dirs_o = ('{}/{}'.format(
        root_dir_o, x[len(common_prefix_i):].lstrip('/')
    ) for x in dirs_i)
    common_prefix_o = '{}/{}'.format(
        root_dir_o,
        common_prefix_i[len(root_dir_i):].lstrip('/')
    )
    os.makedirs(common_prefix_o, exist_ok=True)
    
    # print(root_dir_i, root_dir_o, dirs_i, common_prefix_i)
    
    for d in sorted(dirs_o):
        print(d)
        os.makedirs(d, exist_ok=True)
        if add_init_file:
            with open(f'{d}/__init__.py', 'w', encoding='utf-8') as f:
                f.write('')
    
    io_map = {}  # {str_file_i: str_file_o, ...}
    for file_i in runtime_info_collection['files']:
        file_o = '{}/{}'.format(
            root_dir_o,
            file_i[len(common_prefix_i):].lstrip('/')
        )
        io_map[file_i] = file_o
    return io_map
