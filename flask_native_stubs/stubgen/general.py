import os.path


def normpath(path: str) -> str:
    return os.path.abspath(os.path.normpath(path)) \
        .replace('\\', '/').rstrip('/')
