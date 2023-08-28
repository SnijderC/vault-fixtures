#!/usr/bin/env python3
import functools
import json
import sys
from types import TracebackType
from typing import IO, Annotated, Type, Union

import hvac
import typer
import yaml
from hvac.exceptions import VaultError

from vault_fix import __version__
from vault_fix._log import Logger, LogLevel
from vault_fix.dump import dump_to_fixture_file
from vault_fix.load import load_fixture_from_file
from vault_fix.serializers import _DeSerializerChoices, _SerializerChoices
from vault_fix.serializers.json import json_deserializer, json_serializer
from vault_fix.serializers.yaml import yaml_deserializer, yaml_serializer

cli = typer.Typer(help="Load or dump data?")


def _get_hvac_client(*, host: str, port: int, token: str, tls: bool) -> hvac.Client:
    scheme = "https://" if tls else "http://"
    client = hvac.Client(url=f"{scheme}{host}:{port}", token=token, timeout=5, verify=tls)
    return client


class _ErrorHandler:
    def __init__(self, log: Logger) -> None:
        self.log = log
        self._close: list[IO] = []

    def __enter__(self) -> "_ErrorHandler":
        return self

    def finally_close(self, fh: IO) -> None:
        self._close.append(fh)

    def __exit__(
        self,
        exc_type: Union[Type[BaseException], None],
        exc_val: Union[BaseException, None],
        exc_tb: Union[TracebackType, None],
    ) -> bool:
        msg: str = ""
        exit_code: int = 0

        if exc_type == KeyboardInterrupt:
            self.log.warning(str(exc_val))
            exit_code = 1
        elif exc_type == VaultError:
            exit_code = 2
            if "no handler for route" in str(exc_val):
                msg = "Unable to connect to the mount point, are you sure it exists?"
            else:
                msg = str(exc_val)
        elif exc_type == json.JSONDecodeError:
            msg = f"Invalid JSON data supplied. {exc_val}"
            exit_code = 3
        elif exc_type == yaml.YAMLError:
            msg = f"Invalid YAML data supplied. {exc_val}"
            exit_code = 5
        elif exc_type == OSError:
            msg = str(exc_val)
            exit_code = 4
        else:
            msg = str(exc_val)
            exit_code = 127

        if exc_type and exc_val and exc_tb:
            self.log.exception(exc_type, exc_val, exc_tb)
            self.log.critical(msg)
        for fh in self._close:
            if fh not in (sys.stdin, sys.stdout):
                fh.close()
        typer.Exit(exit_code)
        return True


@cli.command(help="Print the vault-fix version and exit.")
def version():
    print(f"vault-fix v{__version__}")


@cli.command(help="Load up, and dump secrets to and from Vault.")
def dump(
    mount: Annotated[str, typer.Argument(help="Vault mount")],
    path: Annotated[str, typer.Argument(help="Vault path within the mount")],
    token: Annotated[str, typer.Option("--token", "-t", prompt=True, hide_input=True, help="Vault access token.")],
    host: Annotated[str, typer.Option("--host", "-H", help="Vault hostname")] = "localhost",
    port: Annotated[int, typer.Option("--port", "-P", help="Vault network port.")] = 8200,
    tls: Annotated[bool, typer.Option(help="Enable or disable TLS")] = True,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Specify verbosity level by passing more 1 or more -v -vv -vvv's",
        ),
    ] = 0,
    file: Annotated[
        str,
        typer.Option(
            "-f",
            "--file",
            help="Output file, stdout if not specified",
        ),
    ] = "-",
    password: Annotated[
        str,
        typer.Option(
            "--password",
            "-p",
            prompt=True,
            confirmation_prompt=True,
            hide_input=True,
            show_default=False,
            prompt_required=False,
            help="Password to encrypt the dumped fixture, or none for plain text output.",
        ),
    ] = "",
    pretty: Annotated[bool, typer.Option(help="Pretty print the output (if JSON formatted")] = True,
    serializer: Annotated[
        _SerializerChoices, typer.Option(help="Which serializer do you prefer? [default=yaml]")
    ] = _SerializerChoices.yaml,
    dry: Annotated[
        bool,
        typer.Option(
            "-d",
            "--dry",
            help=(
                "Do a dry-run, fetches the secrets and, serializes the data and optionally encrypts it but does not "
                "store it in the output file."
            ),
        ),
    ] = False,
) -> None:
    log = Logger(log_level=LogLevel(verbose))
    mount = mount.strip("/")
    _serializer = yaml_serializer
    if serializer == "json":
        _serializer = functools.partial(json_serializer, pretty=pretty)
    with _ErrorHandler(log) as error_handler:
        client = _get_hvac_client(host=host, port=port, token=token, tls=tls)
        fh = sys.stdout if file == "-" else open(file, "wt", encoding="utf-8")
        error_handler.finally_close(fh)
        dump_to_fixture_file(
            hvac=client,
            fixture=fh,
            mount_point=mount,
            serializer=_serializer,
            path=path,
            password=password or None,
            dry_run=dry,
        )


@cli.command(help="Load up, and dump secrets to and from Vault.")
def load(
    mount: Annotated[str, typer.Argument(help="Vault mount")],
    path: Annotated[str, typer.Argument(help="Vault path within the mount")],
    token: Annotated[str, typer.Option("--token", "-t", prompt=True, hide_input=True, help="Vault access token.")],
    host: Annotated[str, typer.Option("--host", "-H", help="Vault hostname")] = "localhost",
    port: Annotated[int, typer.Option("--port", "-P", help="Vault network port.")] = 8200,
    tls: Annotated[bool, typer.Option(help="Enable or disable TLS")] = True,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            count=True,
            help="Specify verbosity level by passing more 1 or more -v -vv -vvv's",
        ),
    ] = 0,
    file: Annotated[str, typer.Option("-f", "--file", help="Input file, assumes stdin if not specified")] = "-",
    password: Annotated[
        str,
        typer.Option(
            "--password",
            "-p",
            prompt=True,
            hide_input=True,
            show_default=False,
            prompt_required=False,
            help="Password to decrypt the dumped fixture, or none for plain text input.",
        ),
    ] = "",
    deserializer: Annotated[
        _DeSerializerChoices, typer.Option(help="Which deserializer does the fixture file require?")
    ] = _DeSerializerChoices.auto,
    dry: Annotated[
        bool,
        typer.Option(
            "-d",
            "--dry",
            help=(
                "Do a dry-run, parses the file and does the load up to the point where vault is updated with the"
                " secrets."
            ),
        ),
    ] = False,
) -> None:
    log = Logger(log_level=LogLevel(verbose))
    mount = mount.strip("/")
    with _ErrorHandler(log) as error_handler:
        client = _get_hvac_client(host=host, port=port, token=token, tls=tls)

        if file != "-" and not file.endswith((".yml", ".yaml", ".json")):
            raise RuntimeError("Invalid vault fixture file type, should be a YAML or JSON file.")

        fh = sys.stdin if file == "-" else open(file, "rt", encoding="utf-8")
        error_handler.finally_close(fh)
        if deserializer == "auto":
            if file == "-":
                if fh.read(1) == "{":
                    _deserializer = json_deserializer
                else:
                    _deserializer = yaml_deserializer
                fh.seek(0)
            elif file.endswith(".json"):
                _deserializer = json_deserializer
            else:
                _deserializer = yaml_deserializer
        else:
            _deserializer = yaml_deserializer if deserializer == "yaml" else json_deserializer

        load_fixture_from_file(
            hvac=client,
            fixture=fh,
            mount_point=mount,
            deserializer=_deserializer,
            path=path,
            password=password or None,
            dry_run=dry,
        )
