import requests

# Slightly over one TCP retransmission window.
# https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
CONNECT_TIMEOUT_IN_SECONDS = 3.05


def get(url: str, *, timeout: float, **kwargs):
    return requests.get(url, timeout=(CONNECT_TIMEOUT_IN_SECONDS, timeout), **kwargs)


def post(url: str, *, timeout: float, **kwargs):
    return requests.post(url, timeout=(CONNECT_TIMEOUT_IN_SECONDS, timeout), **kwargs)
