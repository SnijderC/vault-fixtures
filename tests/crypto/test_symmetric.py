from unittest import mock

import pytest

from core import crypto
from core.crypto.constants import AESKeySize

PASSWORD = "hunter2"
SECRET_MESSAGE = "Some day this will be replaced by my lattice-based crypto"
ENCRYPTED_SECRET_MESSAGE = (
    "AgCBEAEAAABTU1NTU1NTU1NTU1NTU1NTTk5OTk5OTk5OTk5OFEwDr/XfJIqIcrX6qrFIS/Kmgf"
    "KRMfYpJhtGLjCIT6YwKY4RRMrvT93JqJ0qb9mBkpWlGyeAi7pBB64RvbYg/584d+fgkNEvtQ=="
)


@pytest.fixture()
def mock_pbkdf2_iterations():
    with mock.patch("core.crypto.symmetric.PBKDF2_ITERATIONS", 1) as patched:
        yield patched


def test_encrypt(mock_urandom, mock_pbkdf2_iterations):
    cipher = crypto.SymmetricCrypto(PASSWORD)
    encrypted = cipher.encrypt(SECRET_MESSAGE)
    assert encrypted == ENCRYPTED_SECRET_MESSAGE


def test_decrypt(mock_urandom, mock_pbkdf2_iterations):
    cipher = crypto.SymmetricCrypto(PASSWORD)
    decrypted = cipher.decrypt(ENCRYPTED_SECRET_MESSAGE)
    assert decrypted == SECRET_MESSAGE


def test_decrypt_bad_pass(mock_urandom, mock_pbkdf2_iterations):
    cipher = crypto.SymmetricCrypto("WRONG")
    with pytest.raises(ValueError, match="Failed to decrypt, bad message or password."):
        cipher.decrypt(ENCRYPTED_SECRET_MESSAGE)


@pytest.mark.parametrize("message", [i * "X" for i in range(0, 12, 3)])
@pytest.mark.parametrize("key_size", list(AESKeySize))
def test_keysizes(key_size, message, mock_pbkdf2_iterations):
    cipher = crypto.SymmetricCrypto(PASSWORD)
    encrypted = cipher.encrypt(message, key_size=key_size)
    cipher = crypto.SymmetricCrypto(PASSWORD)
    decrypted = cipher.decrypt(encrypted)
    assert decrypted == message