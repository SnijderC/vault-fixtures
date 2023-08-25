import functools
from typing import Callable
from unittest import mock

import hvac
import pytest
from typer.testing import CliRunner
from vault_fix.__main__ import cli
from vault_fix.serializers.json import json_serializer
from vault_fix.serializers.yaml import yaml_serializer
from vault_fix.type import NestedStrDict

from tests.unit.fixtures import DUMPED_DATA_ENCRYPTED, DUMPED_DATA_PLAIN

runner = CliRunner(mix_stderr=False)


@pytest.mark.parametrize(
    "serializer_args, serializer",
    [
        pytest.param(["--serializer", "json"], functools.partial(json_serializer, pretty=True), id="JSON-pretty"),
        pytest.param(["--serializer", "json", "--no-pretty"], json_serializer, id="JSON-dense"),
        pytest.param(["--serializer", "yaml"], yaml_serializer, id="YAML"),
    ],
)
@pytest.mark.parametrize(
    "password_args, expected",
    [
        pytest.param(["-p", "donttellanyone"], DUMPED_DATA_ENCRYPTED, id="encrypted"),
        pytest.param([], DUMPED_DATA_PLAIN, id="plain"),
    ],
)
def test_dump_to_fixture_file_cli(
    mock_hvac: hvac.Client,
    mock_urandom: mock.Mock,
    serializer_args: list[str],
    password_args: list[str],
    serializer: Callable[[NestedStrDict], str],
    expected: NestedStrDict,
) -> None:
    with mock.patch("vault_fix.__main__.get_hvac_client", return_value=mock_hvac):
        args = ["dump", "secret", "/", *serializer_args, *password_args, "-t", "root"]
        result = runner.invoke(cli, args=args)
    assert result.exit_code == 0
    assert result.stdout == serializer(expected)
