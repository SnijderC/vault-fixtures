import functools
import io
from typing import Any, Callable
from unittest import mock

import hvac
import pytest
from vault_fix.dump import dump, dump_to_fixture_file
from vault_fix.serializers.json import json_serializer
from vault_fix.serializers.yaml import yaml_serializer

from tests.unit.fixtures import DUMPED_DATA_ENCRYPTED, DUMPED_DATA_PLAIN


def test_dump(mock_hvac: hvac.Client) -> None:
    data = dump(hvac=mock_hvac, mount_point="secret", path="/")
    assert data == DUMPED_DATA_PLAIN


@pytest.mark.parametrize(
    "serializer",
    [
        pytest.param(functools.partial(json_serializer, pretty=True), id="JSON-pretty"),
        pytest.param(json_serializer, id="JSON-dense"),
        pytest.param(yaml_serializer, id="YAML"),
    ],
)
@pytest.mark.parametrize(
    "password, expected",
    [
        pytest.param("donttellanyone", DUMPED_DATA_ENCRYPTED, id="encrypted"),
        pytest.param(None, DUMPED_DATA_PLAIN, id="plain"),
    ],
)
def test_dump_to_fixture_file(
    mock_hvac: hvac.Client,
    mock_urandom: mock.Mock,
    serializer: Callable[[dict[str, Any]], str],
    password: str,
    expected: dict[str, Any],
) -> None:
    data = io.StringIO()
    dump_to_fixture_file(
        hvac=mock_hvac,
        fixture=data,
        mount_point="secret",
        path="/",
        serializer=serializer,
        password=password,
    )
    data.seek(0)
    assert data.read() == serializer(expected)


@pytest.mark.parametrize(
    "path",
    [
        pytest.param("10-things-they-dont-want-you-to-know/advertisement", id="slash-no-prefix+no-suffix"),
        pytest.param("/10-things-they-dont-want-you-to-know/advertisement", id="slash-prefix+no-suffix"),
        pytest.param("/10-things-they-dont-want-you-to-know/advertisement/", id="slash-prefix+suffix"),
        pytest.param("10-things-they-dont-want-you-to-know/advertisement/", id="slash-no-prefix+suffix"),
    ],
)
def test_dump_from_fixture_path(path: str) -> None:
    mock_hvac = mock.Mock(spec=hvac.Client)
    mock_hvac.secrets.kv.v2.list_secrets.side_effect = [
        {"data": {"keys": ["annoying-popup-secret"]}},
    ]
    mock_hvac.secrets.kv.v2.read_secret_version.side_effect = [
        {"data": {"data": {"pop-up-secret": "close-button-doesnt-work"}}},
    ]
    data = io.StringIO()
    with mock.patch("vault_fix.__main__._get_hvac_client", return_value=mock_hvac):
        dump_to_fixture_file(
            hvac=mock_hvac,
            fixture=data,
            mount_point="secret",
            path=path,
            serializer=yaml_serializer,
            password=None,
        )
    mock_hvac.secrets.kv.v2.list_secrets.assert_called_once_with(
        path="10-things-they-dont-want-you-to-know/advertisement",
        mount_point="secret",
    )
    mock_hvac.secrets.kv.v2.read_secret_version.assert_called_once_with(
        path="10-things-they-dont-want-you-to-know/advertisement/annoying-popup-secret",
        mount_point="secret",
    )
