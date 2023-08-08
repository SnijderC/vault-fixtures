from unittest import mock

import pytest


@pytest.fixture
def mock_urandom():
    with mock.patch("os.urandom") as patched:
        patched.side_effect = lambda n: (n * "S").encode() if n == 16 else (n * "N").encode()
        yield patched
