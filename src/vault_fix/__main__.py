#!/usr/bin/env python3
import contextlib
import functools
import json
import logging
import re
import sys
from typing import Annotated, Any, Generator

import hvac
import typer
import yaml
from hvac.exceptions import VaultError

from vault_fix import __version__
from vault_fix.dump import dump_to_fixture_file
from vault_fix.load import load_fixture_from_file
from vault_fix.log import get_log_level, get_logger
from vault_fix.serializers import DeSerializerChoices, SerializerChoices
from vault_fix.serializers.json import json_deserializer, json_serializer
from vault_fix.serializers.yaml import yaml_deserializer, yaml_serializer

cli = typer.Typer(help="Load or dump data?")


def get_hvac_client(host: str, port: int, token: str, tls: bool) -> hvac.Client:
    scheme = "https://" if tls else "http://"
    client = hvac.Client(url=f"{scheme}{host}:{port}", token=token, timeout=5, verify=tls)
    return client


class RegexEqual(str):
    def __eq__(self, pattern) -> bool:
        return bool(re.search(pattern, self))


@contextlib.contextmanager
def error_handler(log: logging.Logger) -> Generator[None, Any, None]:
    try:
        yield
    except KeyboardInterrupt as exc:
        log.warning(exc)
        typer.Exit(1)
    except VaultError as exc:
        match RegexEqual(str(exc)):
            case "no handler for route":
                log.critical("Unable to connect to the mount point, are you sure it exists?")
            case _:
                log.critical(exc)
        typer.Exit(2)
    except json.JSONDecodeError as exc:
        log.critical(f"Invalid JSON data supplied. {exc}", exc_info=log.level < 30)
        typer.Exit(3)
    except yaml.YAMLError as exc:
        log.critical(f"Invalid YAML data supplied. {exc}", exc_info=log.level < 30)
        typer.Exit(5)
    except OSError as exc:
        log.critical(exc, exc_info=log.level < 30)
        typer.Exit(4)
    except Exception as exc:
        log.critical(exc, exc_info=log.level < 30)
        if log.level <= logging.DEBUG:
            raise exc
        typer.Exit(127)


@cli.command(help="Print the vault-fix version and exit.")
def version():
    logging.basicConfig(format="%(message)s")
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.info(f"vault-fix v{__version__}")


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
        SerializerChoices, typer.Option(help="Which serializer do you prefer? [default=yaml]")
    ] = SerializerChoices.yaml,
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
    log_level = get_log_level(verbose)
    log = get_logger(__name__, log_level)
    mount = mount.strip("/")
    _serializer = yaml_serializer
    if serializer == "json":
        _serializer = functools.partial(json_serializer, pretty=pretty)
    with error_handler(log):
        client = get_hvac_client(host=host, port=port, token=token, tls=tls)
        fh = sys.stdout if file == "-" else open(file, "wt", encoding="utf-8")
        try:
            dump_to_fixture_file(
                hvac=client,
                fixture=fh,
                mount_point=mount,
                serializer=_serializer,
                path=path,
                password=password or None,
                dry_run=dry,
            )
        finally:
            if fh is not sys.stdout:
                fh.close()


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
        DeSerializerChoices, typer.Option(help="Which deserializer does the fixture file require?")
    ] = DeSerializerChoices.auto,
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
    log_level = get_log_level(verbose)
    log = get_logger(__name__, log_level)
    mount = mount.strip("/")
    with error_handler(log):
        client = get_hvac_client(host=host, port=port, token=token, tls=tls)

        if file != "-" and not file.endswith((".yml", ".yaml", ".json")):
            raise RuntimeError("Invalid vault fixture file type, should be a YAML or JSON file.")

        if deserializer == "auto" and file.endswith(".json"):
            _deserializer = json_deserializer
        else:
            _deserializer = yaml_deserializer if deserializer == "auto" else json_deserializer

        fh = sys.stdin if file == "-" else open(file, "rt", encoding="utf-8")
        try:
            load_fixture_from_file(
                hvac=client,
                fixture=fh,
                mount_point=mount,
                deserializer=_deserializer,
                path=path,
                password=password or None,
                dry_run=dry,
            )
        finally:
            if fh is not sys.stdin:
                fh.close()
