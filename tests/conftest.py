from typing import Any, Generator
from unittest import mock

import hvac
import pytest


@pytest.fixture
def mock_urandom() -> Generator[mock.MagicMock, Any, None]:
    """
    Mocking urandom in order to make salts predictable, making it possible to compare cipher tests from different runs.
    """
    with mock.patch("os.urandom") as patched:
        patched.side_effect = lambda n: (n * "S").encode() if n == 16 else (n * "N").encode()
        yield patched


@pytest.fixture
def mock_hvac() -> mock.Mock:
    client = mock.Mock(spec=hvac.Client)
    client.secrets.kv.v2.list_secrets.side_effect = [
        {"data": {"keys": ["10-things-they-dont-want-you-to-know/"]}},
        {"data": {"keys": ["advertisement/", "something-you-already-know/"]}},
        {"data": {"keys": ["annoying-popup-secret"]}},
        {"data": {"keys": ["secret-things-you-already-know"]}},
    ]
    client.secrets.kv.v2.read_secret_version.side_effect = [
        {"data": {"data": {"pop-up-secret": "close-button-doesnt-work"}}},
        {"data": {"data": {"you-know-this": "click-bait-is-lame"}}},
    ]
    return client
