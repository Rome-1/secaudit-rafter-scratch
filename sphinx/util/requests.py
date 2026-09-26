"""Simple requests package loader"""

from __future__ import annotations

import atexit
import threading
import warnings
from contextlib import contextmanager
from typing import Any, Iterator
from urllib.parse import urlsplit

import requests
from urllib3.exceptions import InsecureRequestWarning

import sphinx

_USER_AGENT = (f'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0 '
               f'Sphinx/{sphinx.__version__}')

# Thread-local storage for sessions
_thread_local = threading.local()


def get_session() -> requests.Session:
    """Get or create a thread-local requests.Session for connection pooling.
    
    This ensures that each thread has its own session, which is important for
    thread safety when making concurrent requests.
    """
    if not hasattr(_thread_local, "session"):
        _thread_local.session = requests.Session()
    return _thread_local.session


# Register a cleanup function to close all sessions at exit
@atexit.register
def _cleanup_sessions() -> None:
    """Close all sessions when the program exits."""
    if hasattr(_thread_local, "session"):
        _thread_local.session.close()


@contextmanager
def ignore_insecure_warning(verify: bool) -> Iterator[None]:
    with warnings.catch_warnings():
        if not verify:
            # ignore InsecureRequestWarning if verify=False
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        yield


def _get_tls_cacert(url: str, certs: str | dict[str, str] | None) -> str | bool:
    """Get additional CA cert for a specific URL."""
    if not certs:
        return True
    elif isinstance(certs, (str, tuple)):
        return certs
    else:
        hostname = urlsplit(url).netloc
        if '@' in hostname:
            _, hostname = hostname.split('@', 1)

        return certs.get(hostname, True)


def get(url: str,
        _user_agent: str = '',
        _tls_info: tuple[bool, str | dict[str, str] | None] = (),  # type: ignore[assignment]
        **kwargs: Any) -> requests.Response:
    """Sends a GET request using the session.

    This sets up User-Agent header and TLS verification automatically."""
    headers = kwargs.setdefault('headers', {})
    headers.setdefault('User-Agent', _user_agent or _USER_AGENT)
    if _tls_info:
        tls_verify, tls_cacerts = _tls_info
        verify = bool(kwargs.get('verify', tls_verify))
        kwargs.setdefault('verify', verify and _get_tls_cacert(url, tls_cacerts))
    else:
        verify = kwargs.get('verify', True)

    with ignore_insecure_warning(verify):
        return get_session().get(url, **kwargs)


def head(url: str,
         _user_agent: str = '',
         _tls_info: tuple[bool, str | dict[str, str] | None] = (),  # type: ignore[assignment]
         **kwargs: Any) -> requests.Response:
    """Sends a HEAD request using the session.

    This sets up User-Agent header and TLS verification automatically."""
    headers = kwargs.setdefault('headers', {})
    headers.setdefault('User-Agent', _user_agent or _USER_AGENT)
    if _tls_info:
        tls_verify, tls_cacerts = _tls_info
        verify = bool(kwargs.get('verify', tls_verify))
        kwargs.setdefault('verify', verify and _get_tls_cacert(url, tls_cacerts))
    else:
        verify = kwargs.get('verify', True)

    with ignore_insecure_warning(verify):
        return get_session().head(url, **kwargs)
