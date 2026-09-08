import os

import httpx
import pytest


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"{name} não configurado; ambiente de teste ainda indisponível")
    return value.rstrip("/")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    """Base da API incluindo /api/v1, por exemplo http://127.0.0.1:8000/api/v1."""
    return _required_env("NOC_API_BASE_URL")


@pytest.fixture(scope="session")
def web_base_url() -> str:
    return _required_env("NOC_WEB_BASE_URL")


@pytest.fixture(scope="session")
def api_client(api_base_url: str):
    with httpx.Client(base_url=api_base_url, timeout=10.0) as client:
        yield client
