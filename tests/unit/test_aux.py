from unittest import mock

import pytest
from vault_fix.__main__ import _get_hvac_client


@pytest.mark.parametrize(
    "host,port,tls,token,expected_url",
    [
        ["localhost", 8200, False, "root", "http://localhost:8200"],
        ["vault.domain.local", 8200, True, "abcd", "https://vault.domain.local"],
    ],
)
def test__get_hvac_client(host: str, port: int, tls: bool, token: str, expected_url: str) -> None:
    with mock.patch("vault_fix.__main__.hvac.Client"):
        client = _get_hvac_client(host=host, port=port, token=token, tls=tls)

        assert client.called_with(url=expected_url, token=token, timeout=5, verify=tls)
