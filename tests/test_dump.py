import functools
import io
from typing import Callable
from unittest import mock

import hvac
import pytest
from vault_fix.dump import dump, dump_to_fixture_file
from vault_fix.serializers.json import json_serializer
from vault_fix.serializers.yaml import yaml_serializer
from vault_fix.type import NestedStrDict

from tests.fixtures import DUMPED_DATA_ENCRYPTED, DUMPED_DATA_PLAIN


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
    serializer: Callable[[NestedStrDict], str],
    password: str,
    expected: NestedStrDict,
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
