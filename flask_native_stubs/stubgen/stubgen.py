"""
collect runtime info, generate stub files.
usage: `~/docs/how-to-generate-python-stub-files-(pyi).zh.md`.
"""
from __future__ import annotations

import os
import typing as t
from textwrap import dedent

from .general import normpath
from .runtime_collector import runtime_info


class T:
    _FilePath = str
    _FileOrDirPath = str
    
    CustomMap = dict[_FileOrDirPath, _FileOrDirPath]
    CustomFilter = t.Sequence[_FileOrDirPath]
    IOMap = dict[_FilePath, _FilePath]


def generate_stubs(
        dir_i: str,
        dir_o: str,
        custom_map: dict = None,
        custom_filter=None,
        add_init_files=True,
        reset_runtime_collector=True,
) -> bool:
    """
    return: bool.
        return True for succeed, False for failed.
    """
    from ..config import STUBGEN_MODE
    if STUBGEN_MODE is False:
        print(':v4', 'You forgot to setup stubgen mode. Please set '
                     '`flask_native_stubs.config.STUBGEN_MODE` to True before '
                     'running `generate_stubs`.')
        exit(0)
    
    dir_i, dir_o = map(normpath, (dir_i, dir_o))
    # print(dir_i, dir_o, runtime_info, ':l')
    
    if not os.path.exists(dir_o): os.mkdir(dir_o)
    io_map = _build_io_map(dir_i, dir_o, custom_map, custom_filter)
    
    def adapt_type(t: str) -> str:
        if t == 'any':
            return 'Any'
        elif t == 'none':
            return 'None'
        else:
            return t
    
    for file_i, file_o in io_map.items():
        function_names = []
        function_defs = []
        for func_name, info in runtime_info[file_i].items():
            function_names.append(func_name)
            function_defs.append('def {}({}) -> {}: ...'.format(
                func_name,
                # TODO: how to add `*args` and `**kwargs`?
                ', '.join((
                    *(f'{x}: {adapt_type(y)}'
                      for x, y in info['args']),
                    *(f'{x}: {adapt_type(y)} = {z}'
                      for x, y, z in info['kwargs']),
                )),
                adapt_type(info['return']),
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
        _add_init_files(dir_o)
    
    # reset runtime_info
    if reset_runtime_collector:
        runtime_info.clear()
    
    return True


def _build_io_map(root_dir_i: str, root_dir_o: str,
                  custom_map: T.CustomMap = None,
                  custom_filter: T.CustomFilter = None) -> T.IOMap:
    """
    args:
        custom_map: dict[str path_i, str path_o]
            the path could either be relative or absolute.
            the path could either be a file or a directory.
        custom_filter: sequence[str relpath, ...]
            the relpath is against root_dir_i.
    """
    # normalize custom filter.
    if custom_filter is None:
        custom_filter = ()
    else:
        custom_filter = tuple(sorted(
            normpath(os.path.join(root_dir_i, x)) + '/'
            for x in custom_filter
        ))
    
    # reformat custom map.
    if custom_map is None:
        custom_map = {}
    else:
        old_map = custom_map
        new_map = {}  # dict[str file_i, str file_o]
        for k in sorted(old_map.keys()):
            # k is either relpath or abspath, we need to convert it to normpath.
            if os.path.isabs(k):
                path_i = normpath(k)
            else:
                path_i = normpath(os.path.join(root_dir_i, k))
            if os.path.isabs(v := old_map[k]):
                path_o = normpath(v)
            else:
                path_o = normpath(os.path.join(root_dir_o, v))
            
            # if path_i is dir (means path_o is also a dir), we add all its
            # children *files* to the map.
            if (path_i + '/').startswith(custom_filter):
                continue
            if os.path.isdir(path_i):
                dir_i = path_i
                dir_o = path_o
                # walk the directory and collect all files
                for root, dirs, files in os.walk(dir_i):
                    sub_dir_i = normpath(root)
                    sub_dir_o = sub_dir_i.replace(dir_i, dir_o, 1)
                    if (sub_dir_i + '/').startswith(custom_filter):
                        continue
                    for name in files:
                        file_i = f'{sub_dir_i}/{name}'
                        file_o = f'{sub_dir_o}/{name}'
                        if (file_i + '/').startswith(custom_filter):
                            continue
                        new_map[file_i] = file_o
            else:
                file_i = path_i
                file_o = path_o
                new_map[file_i] = file_o
        custom_map = new_map
    
    # print(':vl', 'The formatted custom map', custom_map)
    del custom_filter
    
    # -------------------------------------------------------------------------
    
    def find_common_dir_i() -> str:
        dirs_i = filter(lambda x: x.startswith(root_dir_i),
                        set(map(os.path.dirname, runtime_info)))
        common_dir_i = os.path.commonpath(tuple(dirs_i)).rstrip('/')
        assert common_dir_i == root_dir_i or common_dir_i.startswith(root_dir_i)
        # print(root_dir_i, common_dir_i, root_dir_o, ':l')
        return common_dir_i
    
    common_dir_i = find_common_dir_i()
    out: T.IOMap = {}  # dict[str file_i, str file_o]
    
    for file_i in runtime_info.keys():
        if not file_i.startswith(root_dir_i + '/'):
            # print('Skip unscoped file', file_i)
            continue
        if file_i in custom_map:
            file_o = custom_map[file_i]
        else:
            file_o = file_i.replace(common_dir_i, root_dir_o, 1)
        out[file_i] = file_o
    
    print(':v2l', 'The complete IO map is:', {
        k.replace(root_dir_i, '~', 1): v.replace(root_dir_o, '~', 1)
        for k, v in out.items()
    })
    
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
