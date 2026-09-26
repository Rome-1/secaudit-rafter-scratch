import requests


def fetch(url, timeout=10):
    """Fetch a URL and return its body."""
    resp = requests.get(url, timeout=timeout, verify=False)
    resp.raise_for_status()
    return resp.text
