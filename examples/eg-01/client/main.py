"""
python3 main.py
"""
import sys
sys.path.append('.')
sys.path.append('../../..')

from flask_native_stubs import setup
from server_stubs.main import hello

setup('localhost', 5001)


def main():
    result = hello(123, '456', 7.89, d=False)
    print(result)


if __name__ == '__main__':
    main()
