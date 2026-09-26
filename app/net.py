import requests


def fetch(url):
    """Fetch a URL and return its body."""
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text
