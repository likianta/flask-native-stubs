from .runtime_stubgen import generate_stub_files
from .runtime_stubgen import runtime_info_collection


# static_stubgen is not implemented.


def enable_stubgen(project_root_path: str):
    import os.path
    from .. import global_controls as gc
    from ..server_side import app
    
    runtime_info_collection['root_path'] = os.path.abspath(project_root_path)
    
    gc.COLLECT_RUNTIME_INFO = True
    gc.SIMULATION_MODE = True
    
    def _simulation_run(*_, **__):
        raise Exception('flask is under simulation mode, '
                        '`app.run` is disabled!')
    
    setattr(app, 'run', _simulation_run)
