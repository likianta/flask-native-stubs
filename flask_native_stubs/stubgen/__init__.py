"""
note:
    runtime_stubgen: collect runtime information.
    static_stubgen: not implemented yet.

workflow:
    1. set an entrance directory to watch.
    2. caller explicitly calls (or just imports) modules who are decorated by
       flask_native_stubs. flask_native_stubs will detect them and record their
       info to `.runtime_stubgen > runtime_info_collection` dict.
    3. export collected info to output directory.
    4. (optional) reset `runtime_info_collection` dict.
"""
from contextlib import contextmanager

from .runtime_stubgen import generate_stub_files
from .runtime_stubgen import runtime_info_collection
from ..server_side import app


def enable_stubgen(watch_directory: str):
    import os.path
    from .. import global_controls as gc
    
    runtime_info_collection['root_path'] = os.path.abspath(watch_directory)
    
    gc.COLLECT_RUNTIME_INFO = True
    gc.SIMULATION_MODE = True
    
    _disable_app_run()


@contextmanager
def watch_directory(directory: str):
    """ another way as a replacement of `enable_stubgen`. """
    from .runtime_stubgen import reset_runtime_info_collection
    enable_stubgen(directory)
    yield
    reset_runtime_info_collection()
    _enable_app_run()


# -----------------------------------------------------------------------------

_app_run_backup = app.run


def _disable_app_run():
    def _disabled_run(*_, **__):
        raise Exception('flask-native-stubs is under simulation mode, '
                        '`app.run` is disabled!')
    
    setattr(app, 'run', _disabled_run)


def _enable_app_run():
    setattr(app, 'run', _app_run_backup)
