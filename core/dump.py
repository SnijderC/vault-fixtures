from typing import Callable, TextIO

import hvac

from core.crypto import encrypt_fixture_data
from core.crypto.symmetric import SymmetricCrypto
from core.type import NestedStrDict


def dump_to_fixture_file(
    *,
    hvac: hvac.Client,
    fixture: TextIO,
    mount_point,
    serializer: Callable[[NestedStrDict], str],
    path: str = "/",
    password: str | None = None,
):
    # json.dump works too, but makes testing much harder that it has to be.
    fixture_data = dump(
        hvac=hvac,
        mount_point=mount_point,
        path=path,
    )
    if password:
        cipher = SymmetricCrypto(password)
        fixture_data = encrypt_fixture_data(fixture_data, cipher)
    fixture.write(serializer(fixture_data))


def dump(*, hvac: hvac.Client, mount_point: str, path: str) -> NestedStrDict:
    """
    Dump all secrets in the hierarchy under ``path`` to a dict.

    NOTE: This method is relatively slow because it recursively discovers secrets data from Vault.

    :param hvac: Initialised hvac.Client object.
    :param mount_point: The mount_point in Vault where the secrets are stored.
    :param path: The path in Vault where the secrets are stored.
    :returns: Dictionary of secrets under ``{mount_point}/{path}``.
    """
    key: str
    result = dict()

    vault = hvac.secrets.kv.v2

    keys = vault.list_secrets(path=path, mount_point=mount_point).get("data", {}).get("keys", [])

    for key in keys:
        if key.endswith("/"):
            result[key] = dump(hvac=hvac, path=f"{path}/{key}", mount_point=mount_point)
        else:
            data = vault.read_secret_version(path=f"{path}/{key}", mount_point=mount_point)
            result[key] = data.get("data", {}).get("data", {})

    return result
