import socket
from contextlib import closing
from kernelCI_app.helpers.logger import log_message
import pytest


def ping(host: str, port: int) -> bool:
    """
    Checks if `host` is online by trying to connect to its `port`
    """
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(6)
            return sock.connect_ex((host, port)) == 0
    except socket.gaierror as e:
        log_message(e)
        return False


online = pytest.mark.skipif(not ping("localhost", 8000), reason="Server is not online")
