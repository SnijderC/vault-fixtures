from typing import Any, Generator
from unittest import mock

import pytest
from vault_fix import _crypto
from vault_fix._crypto.constants import AESKeySize

from tests.unit.fixtures import ENCRYPTED_SECRET_MESSAGE, PASSWORD, SECRET_MESSAGE


@pytest.fixture()
def mock_pbkdf2_iterations() -> Generator[int, Any, None]:
    with mock.patch("vault_fix._crypto.symmetric.PBKDF2_ITERATIONS", 1) as patched:
        yield patched


def test_encrypt(mock_urandom, mock_pbkdf2_iterations):
    cipher = _crypto.SymmetricCrypto(PASSWORD)
    encrypted = cipher.encrypt(SECRET_MESSAGE)
    assert encrypted == ENCRYPTED_SECRET_MESSAGE


def test_decrypt(mock_urandom, mock_pbkdf2_iterations):
    cipher = _crypto.SymmetricCrypto(PASSWORD)
    decrypted = cipher.decrypt(ENCRYPTED_SECRET_MESSAGE)
    assert decrypted == SECRET_MESSAGE


def test_decrypt_bad_pass(mock_urandom, mock_pbkdf2_iterations):
    cipher = _crypto.SymmetricCrypto("WRONG")
    with pytest.raises(ValueError, match="Failed to decrypt, bad message or password."):
        cipher.decrypt(ENCRYPTED_SECRET_MESSAGE)


@pytest.mark.parametrize("message", [i * "X" for i in range(0, 12, 3)])
@pytest.mark.parametrize("key_size", list(AESKeySize))
def test_keysizes(key_size, message, mock_pbkdf2_iterations):
    cipher = _crypto.SymmetricCrypto(PASSWORD)
    encrypted = cipher.encrypt(message, key_size=key_size)
    cipher = _crypto.SymmetricCrypto(PASSWORD)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == message
