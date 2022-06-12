"""
python3 temp_stubgen.py
"""
import os
import sys
sys.path.append('..')
sys.path.append('../../..')

sys.path.append('/Users/Likianta/Desktop/workspace/dev_master_likianta/rich-print')
import rich_print  # noqa
rich_print.setup()

from flask_native_stubs import enable_stubgen, generate_stub_files
enable_stubgen('..')

from server import main  # noqa

if not os.path.exists(d := './server_stubs'):
    os.mkdir(d)
generate_stub_files(d)
