import socket
from contextlib import closing
import pytest


def ping(host: str, port: int) -> bool:
    """
    Checks if `host` is online by trying to connect to its `port`
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(6)
        return sock.connect_ex((host, port)) == 0


online = pytest.mark.skipif(not ping("localhost", 8000), reason="Server is not online")
