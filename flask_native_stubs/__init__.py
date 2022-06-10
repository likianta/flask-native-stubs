from . import config
from . import request
from . import stubgen
from .app import app
from .app import auto_route
from .request import setup as setup_client
from .stubgen import enable_stubgen
from .stubgen import generate_stub_files
from .stubgen import watch_directory

__version__ = '1.0.0'
