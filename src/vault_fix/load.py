from typing import Callable, Generator, TextIO, Union

import hvac

from vault_fix._crypto import decrypt_fixture_data
from vault_fix._crypto.symmetric import SymmetricCrypto
from vault_fix._type import NestedStrDict


def load_fixture_from_file(
    *,
    hvac: hvac.Client,
    fixture: TextIO,
    mount_point,
    deserializer: Callable[[TextIO], NestedStrDict],
    path: str = "/",
    password: Union[str, None] = None,
    dry_run: bool = False,
) -> None:
    fixture_data = deserializer(fixture)
    if password:
        cipher = SymmetricCrypto(password)
        fixture_data = decrypt_fixture_data(fixture_data, cipher)
    load(hvac=hvac, fixture=fixture_data, mount_point=mount_point, path=path, dry_run=dry_run)


def load(*, hvac: hvac.Client, fixture: dict, mount_point: str, path: str, dry_run: bool = False) -> None:
    """
    Imports a fixture from a dict.

    Format should be::

        {
            "some/": {
                "path/": {
                    "secret_data": {
                        "username": "IGIgYSBkIHAgYSBzIHMgdwo=",
                        "totp_secret": "IG4gbyBzIGUgYyByIGUgdCAK"
                    }
                }
            }
        }

    :param hvac: Initialised hvac.Client object.
    :param fixture: Secrets data to be imported into Vault.
    :param mount_point: The mount_point in Vault where the secrets should be stored.
    :param path: The path in the fixture file from which you want to import secrets to the same path in Vault.
    """
    parent = ""
    for _path in path.strip("/").split("/"):
        if _path:
            parent = f"{parent}{_path}/"
            fixture = fixture[f"{_path}/"]

    for _path, secrets in _fixture_deserialize(data=fixture, parent=parent):
        if isinstance(secrets, str) and secrets.startswith("encrypted//"):
            raise RuntimeError("Fixture file is encrypted but not password was passed.")
        if not dry_run:
            hvac.secrets.kv.v2.create_or_update_secret(path=_path, secret=secrets, mount_point=mount_point)


def _fixture_deserialize(
    *, data: dict, parent: str = "/"
) -> Generator[tuple[str, Union[str, NestedStrDict]], None, None]:
    """
    Changes a dictionary to a generator of tuples with paths as the first entry and secrets data as the second.

    This works only for structures that have a `/` in keys that are part of the path.

    This is meant to "deserialize" fixtures with a hierarchical structure to a flatter structure, that can be used in
    calls to the Vault API.

    e.g.
    >>> entry = _fixture_deserialize({ "foo/": {"bar/": {"baz": "spam"}}}).__next__()
    >>> assert entry == ('foo/bar/baz', 'spam')

    :param data: Data to deserialize
    :param _parent: Used to keep track of the parent path in recursive deserializing
    """
    for path, _data in data.items():
        if path.endswith("/"):
            for entry in _fixture_deserialize(data=_data, parent=f"{parent}{path}"):
                yield entry
        else:
            yield (f"{parent}{path}", _data)
