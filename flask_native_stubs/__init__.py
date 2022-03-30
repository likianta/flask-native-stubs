from . import global_controls as gc
from . import stubgen
from .client_side import add_route
from .client_side import setup
from .server_side import app
from .server_side import auto_route
from .stubgen import enable_stubgen
from .stubgen import generate_stub_files
from .stubgen import watch_directory

__version__ = '0.2.4'
