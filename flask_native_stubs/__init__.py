from . import api
from . import request
from . import stubgen
from .app import app
from .app import auto_route
from .config import cfg
from .config import setup
from .protocol import CriticalError
from .protocol import WeakError
from .request import session
from .stubgen import generate_stubs

# defer init
from . import _safe_exit

__version__ = '0.5.0'
