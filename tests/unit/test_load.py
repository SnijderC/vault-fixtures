import io
from typing import Callable, TextIO
from unittest import mock

import hvac
import pytest
from vault_fix._type import NestedStrDict
from vault_fix.load import load, load_fixture_from_file
from vault_fix.serializers.json import json_deserializer, json_serializer
from vault_fix.serializers.yaml import yaml_deserializer

from tests.unit.fixtures import DUMPED_DATA_ENCRYPTED, DUMPED_DATA_PLAIN


def test_load(mock_hvac: hvac.Client) -> None:
    load(hvac=mock_hvac, mount_point="secret", path="/", fixture=DUMPED_DATA_PLAIN)


@pytest.mark.parametrize(
    "deserializer",
    [
        pytest.param(json_deserializer, id="JSON"),
        pytest.param(yaml_deserializer, id="YAML"),
    ],
)
@pytest.mark.parametrize(
    "password, fixture",
    [
        pytest.param("donttellanyone", DUMPED_DATA_ENCRYPTED, id="encrypted"),
        pytest.param(None, DUMPED_DATA_PLAIN, id="plain"),
    ],
)
def test_load_from_fixture_file(
    mock_hvac: hvac.Client,
    deserializer: Callable[[TextIO], NestedStrDict],
    password: str,
    fixture: NestedStrDict,
) -> None:
    _fixture = io.StringIO(json_serializer(fixture))
    load_fixture_from_file(
        hvac=mock_hvac,
        fixture=_fixture,
        mount_point="secret",
        path="/",
        deserializer=deserializer,
        password=password,
    )
    assert mock_hvac.secrets.kv.v2.create_or_update_secret.call_count == 2
    mock_hvac.secrets.kv.v2.create_or_update_secret.assert_has_calls(
        [
            mock.call(
                path="10-things-they-dont-want-you-to-know/advertisement/annoying-popup-secret",
                secret={"pop-up-secret": "close-button-doesnt-work"},
                mount_point="secret",
            ),
            mock.call(
                path="10-things-they-dont-want-you-to-know/something-you-already-know/secret-things-you-already-know",
                secret={"you-know-this": "click-bait-is-lame"},
                mount_point="secret",
            ),
        ]
    )


def test_load_from_fixture_encryped_no_password(mock_hvac: hvac.Client):
    with pytest.raises(RuntimeError):
        load_fixture_from_file(
            hvac=mock_hvac,
            fixture=io.StringIO(json_serializer(DUMPED_DATA_ENCRYPTED)),
            mount_point="secret",
            path="/",
            deserializer=json_deserializer,
            password=None,
        )
