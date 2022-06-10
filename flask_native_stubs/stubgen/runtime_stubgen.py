"""
collect runtime info, generate stub files.
usage: `~/docs/how-to-generate-python-stub-files-(pyi).zh.md`.
"""
import os
from collections import defaultdict
from textwrap import dedent
from typing import Union

from .. import config

runtime_info_collection = {
    'root_path': '',
    'files'    : defaultdict(dict)
}
''' {
        'root_path': str abspath,
        'files': {
            str filepath: {  # the filepath is always absolute path.
                str func_name: {
                    # see `../general.py`
                    'args': ...,
                    'kwargs': ...,
                    'has_*args': ...,  # v0.2 doesn't support
                    'has_**kwargs': ...,  # v0.2 doesn't support
                    'return': ...,
                }, ...
            }, ...
        }
    }
'''


def reset_runtime_info_collection():
    runtime_info_collection.clear()
    runtime_info_collection.update({
        'root_path': '',
        'files'    : defaultdict(dict)
    })


def generate_stub_files(
        dir_o: str, io_map: Union[str, dict] = 'tree_map',
        add_init_files=True
) -> bool:  # return True for succeed, False for failed.
    """
    args:
        dir_o: str path. assert exists.
        io_map: str | dict.
            str: 'tree_map' | 'flat_map'.
            dict: dict[str path_i, str path_o].
        add_init_files: bool.
    """
    if config.COLLECT_RUNTIME_INFO is False:
        raise Exception('Runtime info collection is not enabled! '
                        'Did you forget to call `flask_native_stubs'
                        '.enable_stubgen()`?')
    if not runtime_info_collection['files']:
        return False
    
    dir_o = os.path.abspath(dir_o)
    
    # print(runtime_info_collection, ':l')
    
    if isinstance(io_map, str):
        if io_map == 'tree_map':
            io_map = _gen_tree_map(dir_o)
        elif io_map == 'flat_map':
            io_map = _gen_flat_map(dir_o)
        else:
            raise Exception(io_map)
    else:
        io_map = _normalize_io_map(io_map)
    assert isinstance(io_map, dict)
    
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
                from __future__ import annotations
                
                from flask_native_stubs.stubgen import add_route
                from typing import Any
                
                {functions}
                
                [add_route(x) for x in ({function_names},)]
            ''').lstrip().format(
                functions='\n\n'.join(function_defs),
                function_names=', '.join(function_names),
            ))
        print(f'file generated: {file_o}')
    
    if add_init_files:
        _add_init_files(dir_o)
    
    reset_runtime_info_collection()
    return True


# -----------------------------------------------------------------------------

def _gen_tree_map(dir_o: str) -> dict:
    return _create_empty_dirs(dir_o)


def _gen_flat_map(dir_o: str) -> dict:
    os.makedirs(dir_o, exist_ok=True)
    all_file_paths = tuple(runtime_info_collection['files'])
    all_file_names_0 = tuple(map(os.path.basename, all_file_paths))
    all_file_names_1 = set(all_file_names_0)
    
    if len(all_file_names_1) == len(all_file_names_0):
        return {fp: f'{dir_o}/{fn}' for fp, fn in zip(
            all_file_paths, all_file_names_0
        )}
    else:  # collect conflicts, and raise error
        conflicts = [x for x in all_file_names_0 if x not in all_file_names_1]
        raise Exception(
            'Cannot apply `flat_dir` feature: there are duplicate file '
            'names!\n{}'.format('\n'.join(conflicts))
        )


def _normalize_io_map(io_map: dict) -> dict:
    # normalize with abspath.
    io_map = {os.path.abspath(k): os.path.abspath(v)
              for k, v in io_map.items()}
    
    collected_file_paths = tuple(runtime_info_collection['files'])
    defined_paths = tuple(sorted(io_map.keys(), reverse=True))
    
    new_io_map = {}
    
    for fp in collected_file_paths:
        if fp in defined_paths:
            new_io_map[fp] = io_map[fp]
        else:
            for i in defined_paths:
                if fp.startswith(i):
                    file_i = fp
                    file_o = io_map[i] + fp[len(i):]
                    new_io_map[file_i] = file_o
                    break
            else:
                print(':l', fp, defined_paths, collected_file_paths)
                raise Exception(f'Undefined file path: {fp}')
    
    dirs_to_create = set()
    for k, v in new_io_map.items():
        dirs_to_create.add(os.path.dirname(v))
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
    del dirs_to_create
    
    return new_io_map


# -----------------------------------------------------------------------------

def _create_empty_dirs(dir_o: str) -> dict:
    root_dir_i = runtime_info_collection['root_path'].replace('\\', '/')
    root_dir_o = dir_o.replace('\\', '/')
    
    dirs_i = set(
        os.path.dirname(x)
        for x in runtime_info_collection['files']
    )
    common_prefix_i = os.path.commonpath(tuple(dirs_i)).rstrip('/')
    if not common_prefix_i.startswith(root_dir_i):
        print(root_dir_i, root_dir_o, dirs_i, common_prefix_i)
        raise Exception('Some indexed file(s) is/are outside of root dir!')
    
    dirs_o = ('{}/{}'.format(
        root_dir_o, x[len(common_prefix_i):].lstrip('/')
    ) for x in dirs_i)
    common_prefix_o = '{}/{}'.format(
        root_dir_o,
        common_prefix_i[len(root_dir_i):].lstrip('/')
    )
    os.makedirs(common_prefix_o, exist_ok=True)
    
    for d in sorted(dirs_o):
        print(d)
        os.makedirs(d, exist_ok=True)
    
    io_map = {}  # {str_file_i: str_file_o, ...}
    for file_i in runtime_info_collection['files']:
        file_o = '{}/{}'.format(
            root_dir_o,
            file_i[len(common_prefix_i):].lstrip('/')
        )
        io_map[file_i] = file_o
    return io_map


# -----------------------------------------------------------------------------

def _add_init_files(dir_o: str):
    for root, dirs, files in os.walk(dir_o):
        # print(root, dirs, files)
        if root.startswith(('__', '.')):
            continue
        modules = (x[:-3] for x in files
                   if x.endswith('.py')
                   and not x.startswith(('__', '.')))
        print('Add __init__.py', f'{root}/__init__.py')
        with open(f'{root}/__init__.py', 'w', encoding='utf-8') as f:
            f.write('\n'.join((
                'from . import {}'.format(x) for x in modules
            )))
