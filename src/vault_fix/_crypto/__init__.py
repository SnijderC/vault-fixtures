import json

from vault_fix._crypto.symmetric import SymmetricCrypto
from vault_fix._type import NestedStrDict


def decrypt_fixture_data(vaultFixture: dict, cipher: SymmetricCrypto) -> NestedStrDict:
    for path, data in vaultFixture.items():
        if path.endswith("/"):
            vaultFixture[path] = decrypt_fixture_data(data, cipher)
        else:
            vaultFixture[path] = json.loads(cipher.decrypt(data[11:]))
    return vaultFixture


def encrypt_fixture_data(vaultFixture: dict, cipher: SymmetricCrypto) -> NestedStrDict:
    for path, data in vaultFixture.items():
        if path.endswith("/"):
            vaultFixture[path] = encrypt_fixture_data(data, cipher)
        else:
            vaultFixture[path] = f"encrypted//{cipher.encrypt(json.dumps(data, indent=None))}"
    return vaultFixture
