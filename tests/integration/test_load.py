from typing import Any, Generator
from unittest import mock

import hvac
import pytest
from typer.testing import CliRunner
from vault_fix.__main__ import cli

from tests.unit.fixtures import JSON_DUMPED_ENCRYPTED, JSON_DUMPED_PLAIN, YAML_DUMPED_ENCRYPTED, YAML_DUMPED_PLAIN

runner = CliRunner(mix_stderr=False)


@pytest.fixture
def file_data(request) -> Generator[Any, Any, None]:
    with mock.patch("builtins.open", mock.mock_open(read_data=request.param)) as mock_open:
        yield mock_open


@pytest.mark.parametrize(
    "deserializer_args, password_args, stdin_data",
    [
        pytest.param(["--deserializer", "json"], [], JSON_DUMPED_PLAIN, id="JSON-plain"),
        pytest.param(
            ["--deserializer", "json"],
            ["-p", "donttellanyone"],
            JSON_DUMPED_ENCRYPTED,
            id="JSON-encrypted",
        ),
        pytest.param(["--deserializer", "yaml"], [], YAML_DUMPED_PLAIN, id="YAML-plain"),
        pytest.param(
            ["--deserializer", "yaml"],
            ["-p", "donttellanyone"],
            YAML_DUMPED_ENCRYPTED,
            id="YAML-encrypted",
        ),
        pytest.param([], [], YAML_DUMPED_PLAIN, id="AUTO-YAML-plain"),
        pytest.param([], ["-p", "donttellanyone"], YAML_DUMPED_ENCRYPTED, id="AUTO-YAML-encrypted"),
        pytest.param([], [], JSON_DUMPED_PLAIN, id="AUTO-JSON-plain"),
        pytest.param([], ["-p", "donttellanyone"], JSON_DUMPED_ENCRYPTED, id="AUTO-JSON-encrypted"),
    ],
)
def test_load_from_fixture_stdin_cli(
    mock_hvac: hvac.Client,
    deserializer_args: list[str],
    password_args: list[str],
    stdin_data: str,
) -> None:
    with mock.patch("vault_fix.__main__._get_hvac_client", return_value=mock_hvac):
        args = ["load", "secret", "/", *deserializer_args, *password_args, "-t", "root"]
        result = runner.invoke(cli, args=args, input=stdin_data)
    assert result.exit_code == 0
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


@pytest.mark.parametrize(
    "deserializer_args, password_args, file, file_data",
    [
        pytest.param(["--deserializer", "json"], [], "fixture.json", JSON_DUMPED_PLAIN, id="JSON-plain"),
        pytest.param(
            ["--deserializer", "json"],
            ["-p", "donttellanyone"],
            "fixture.json",
            JSON_DUMPED_ENCRYPTED,
            id="JSON-encrypted",
        ),
        pytest.param(["--deserializer", "yaml"], [], "fixture.yaml", YAML_DUMPED_PLAIN, id="YAML-plain"),
        pytest.param(
            ["--deserializer", "yaml"],
            ["-p", "donttellanyone"],
            "fixture.yml",
            YAML_DUMPED_ENCRYPTED,
            id="YAML-encrypted",
        ),
        pytest.param([], [], "fixture.yml", YAML_DUMPED_PLAIN, id="AUTO-YAML-plain"),
        pytest.param([], ["-p", "donttellanyone"], "fixture.yaml", YAML_DUMPED_ENCRYPTED, id="AUTO-YAML-encrypted"),
        pytest.param([], [], "fixture.json", JSON_DUMPED_PLAIN, id="AUTO-JSON-plain"),
        pytest.param([], ["-p", "donttellanyone"], "fixture.json", JSON_DUMPED_ENCRYPTED, id="AUTO-JSON-encrypted"),
    ],
    indirect=["file_data"],
)
def test_load_from_fixture_file_cli(
    mock_hvac: hvac.Client,
    file_data,
    deserializer_args: list[str],
    password_args: list[str],
    file: str,
) -> None:
    with mock.patch("vault_fix.__main__._get_hvac_client", return_value=mock_hvac):
        args = ["load", "secret", "/", *deserializer_args, *password_args, "-t", "root", "-f", file]
        result = runner.invoke(cli, args=args)
    assert result.exit_code == 0
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


@pytest.mark.parametrize(
    "deserializer_args, password_args, stdin_data",
    [
        pytest.param(["--deserializer", "json"], [], JSON_DUMPED_PLAIN, id="JSON-plain"),
        pytest.param(["--deserializer", "yaml"], [], YAML_DUMPED_PLAIN, id="YAML-plain"),
    ],
)
def test_load_from_fixture_stdin_cli_path(
    mock_hvac: hvac.Client,
    deserializer_args: list[str],
    password_args: list[str],
    stdin_data: str,
) -> None:
    with mock.patch("vault_fix.__main__._get_hvac_client", return_value=mock_hvac):
        args = [
            "load",
            "secret",
            "/10-things-they-dont-want-you-to-know/advertisement",
            *deserializer_args,
            *password_args,
            "-t",
            "root",
        ]
        result = runner.invoke(cli, args=args, input=stdin_data)
    assert result.exit_code == 0
    assert mock_hvac.secrets.kv.v2.create_or_update_secret.call_count == 1
    mock_hvac.secrets.kv.v2.create_or_update_secret.assert_has_calls(
        [
            mock.call(
                path="10-things-they-dont-want-you-to-know/advertisement/annoying-popup-secret",
                secret={"pop-up-secret": "close-button-doesnt-work"},
                mount_point="secret",
            ),
        ]
    )


@pytest.mark.parametrize(
    "args, file_data, error",
    [
        pytest.param(
            ["-f", "fixture.json"], YAML_DUMPED_ENCRYPTED, "Invalid JSON data supplied", id="YAML-with-json-ext"
        ),
        pytest.param(
            ["-f", "fixture.yaml"],
            YAML_DUMPED_ENCRYPTED,
            "Fixture file is encrypted but not password was passed.",
            id="encrypted-no-password",
        ),
        pytest.param(
            ["-f", "fixture.csv"],
            "",
            "Invalid vault fixture file type, should be a YAML or JSON file.",
            id="Unsupported-file-type",
        ),
    ],
    indirect=["file_data"],
)
def test_load_exceptions(mock_hvac: hvac.Client, file_data, args: list[str], error: str) -> None:
    args = ["load", "secret", "/", "-t", "root", *args]
    with mock.patch("vault_fix.__main__._get_hvac_client", return_value=mock_hvac):
        result = runner.invoke(cli, args=args)
    assert error in result.stderr
