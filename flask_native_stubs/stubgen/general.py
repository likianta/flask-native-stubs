import os.path


def normpath(path: str) -> str:
    return os.path.abspath(path).replace('\\', '/').rstrip('/')
