"""
python3 main.py
"""
import sys
sys.path.append('../../..')

from flask_native_stubs import app
from flask_native_stubs import auto_route


@auto_route()
def hello(a: int, b: str, c: float, d: bool = None) -> list:
    return [a, b, c, d]


if __name__ == '__main__':
    app.run('localhost', 5001)
