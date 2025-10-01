import httpx
from ..core.config import settings

def http_client() -> httpx.Client:
    return httpx.Client(timeout=settings.request_timeout_s)
