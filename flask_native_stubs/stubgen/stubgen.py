"""
collect runtime info, generate stub files.
usage: `~/docs/how-to-generate-python-stub-files-(pyi).zh.md`.
"""
from __future__ import annotations

import os
import typing as t
from collections import defaultdict
from textwrap import dedent

from .general import normpath
from .runtime_collector import runtime_info


class T:
    Path = str
    _FilePath = str
    _FileOrDirPath = str
    
    CustomMap = dict[_FileOrDirPath, _FileOrDirPath]
    IOMap = dict[_FilePath, _FilePath]


def generate_stubs(
        output_dir: str,
        filenames_map: dict = None,
        add_init_files=True,
        reset_runtime_collector=True,
) -> bool:
    """
    return: bool.
        return True for succeed, False for failed.
    """
    # print(runtime_info, ':l')
    
    output_dir = normpath(output_dir)
    assert os.path.exists(output_dir)
    io_map = _build_io_map(output_dir, filenames_map)
    
    def adapt_type(t: str) -> str:
        if t == 'any':
            return 'Any'
        elif t == 'none':
            return 'None'
        else:
            return t
    
    for file, v0 in runtime_info.items():
        file_i = file
        file_o = io_map[file_i]
        
        function_names = []
        function_defs = []
        for func_name, v1 in v0.items():
            function_names.append(func_name)
            function_defs.append('def {}({}) -> {}: ...'.format(
                func_name,
                # TODO: how to add `*args` and `**kwargs`?
                ', '.join((
                    *(f'{x}: {adapt_type(y)}'
                      for x, y in v1['args']),
                    *(f'{x}: {adapt_type(y)} = {z}'
                      for x, y, z in v1['kwargs']),
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
                
                from flask_native_stubs.stubgen import magic_route
                from typing import Any
                
                {functions}
                
                [magic_route(x) for x in ({function_names},)]
            ''').lstrip().format(
                functions='\n\n'.join(function_defs),
                function_names=', '.join(function_names),
            ))
        print(f'File generated: {file_o}')
    
    if add_init_files:
        _add_init_files(output_dir)
    
    # reset runtime_info
    if reset_runtime_collector:
        from . import runtime_collector
        runtime_collector.runtime_info = defaultdict(dict)
    
    return True


def _build_io_map(output_dir: T.Path, custom: T.CustomMap = None) -> T.IOMap:
    """
    args:
        custom: dict[str path_i, str path_o].
            the path could either be relative or absolute.
            the path could either be a file or a directory.
    """
    root_dir_i: str
    root_dir_o: str
    
    dirs_i = set(map(os.path.dirname, runtime_info))
    root_dir_i = os.path.commonpath(tuple(dirs_i)).rstrip('/')
    root_dir_o = output_dir
    
    if custom is None:
        custom = {}
    else:
        old_custom = custom
        new_custom = {}  # dict[str file_i, str file_o]
        for k in sorted(old_custom.keys()):
            path_i = normpath(k)
            path_o = normpath('{}/{}'.format(root_dir_o, old_custom[k]))
            
            if os.path.isdir(path_i):
                dir_i = path_i
                dir_o = path_o
                # walk the directory and collect all files
                for root, dirs, files in os.walk(dir_i):
                    sub_dir_i = normpath(root)
                    sub_dir_o = sub_dir_i.replace(dir_i, dir_o, 1)
                    for name in files:
                        file_i = f'{sub_dir_i}/{name}'
                        file_o = f'{sub_dir_o}/{name}'
                        new_custom[file_i] = file_o
            else:
                file_i = path_i
                file_o = path_o
                new_custom[file_i] = file_o
        custom = new_custom
    
    out: T.IOMap = {}  # dict[str file_i, str file_o]
    
    for file_i in runtime_info.keys():
        if file_i in custom:
            file_o = custom[file_i]
        else:
            file_o = file_i.replace(root_dir_i, root_dir_o, 1)
        out[file_i] = file_o
    
    # create empty directories
    _create_empty_dirs(set(map(os.path.dirname, out.values())))
    
    return out


def _create_empty_dirs(dirs: t.Iterable[str]):
    # create empty directories
    from os import makedirs
    for dir_o in sorted(dirs):
        print(f'Create dir: {dir_o}', ':p')
        makedirs(dir_o, exist_ok=True)


def _add_init_files(output_dir: str):
    for root, dirs, files in os.walk(output_dir):
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
