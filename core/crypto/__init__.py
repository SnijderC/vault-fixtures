import json

from core.crypto.symmetric import SymmetricCrypto
from core.type import NestedStrDict


def decrypt_fixture_data(vaultFixture: dict, cipher: SymmetricCrypto | None = None) -> NestedStrDict:
    for path, data in vaultFixture.items():
        if path.endswith("/"):
            vaultFixture[path] = decrypt_fixture_data(data, cipher)
        else:
            if isinstance(data, str) and data.startswith("encrypted//"):
                if cipher is None:
                    raise RuntimeError(
                        "Fixture has encrypted entries, supply a password in order to import it successfully."
                    )
                vaultFixture[path] = json.loads(cipher.decrypt(data[11:]))
    return vaultFixture


def encrypt_fixture_data(vaultFixture: dict, cipher: SymmetricCrypto) -> NestedStrDict:
    for path, data in vaultFixture.items():
        if path.endswith("/"):
            vaultFixture[path] = encrypt_fixture_data(data, cipher)
        else:
            vaultFixture[path] = f"encrypted//{cipher.encrypt(json.dumps(data, indent=None))}"
    return vaultFixture