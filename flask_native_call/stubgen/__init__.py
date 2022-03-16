from .runtime_stubgen import generate_stub_files
from .runtime_stubgen import runtime_info_collection

# static_stubgen is not implemented.


def enable_stubgen(project_root_path: str):
    from .. import global_controls as gc
    gc.COLLECT_RUNTIME_INFO = True
    runtime_info_collection['root_path'] = project_root_path
