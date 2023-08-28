import pytest
from vault_fix._crypto.constants import VERSION, CipherMode
from vault_fix._crypto.message import CipherMessage

from tests.unit.fixtures import ENCRYPTED_SECRET_MESSAGE


@pytest.fixture
def valid_message():
    return CipherMessage(
        salt=("S" * 16).encode(),
        nonce=("N" * 12).encode(),
        mode=CipherMode.SYMMETRIC | CipherMode.GCM_AEAD,
        pbkdf2_iterations=1000,
        key_size=16,
        version=VERSION,
        cipher_text=b"",
    )


def test_unpack_bad_data():
    with pytest.raises(ValueError, match="Not a valid ciphertext for this module: bad message."):
        CipherMessage.unpack(ENCRYPTED_SECRET_MESSAGE[:20])  # short


@pytest.mark.parametrize(
    "kwargs,_repr",
    [
        ({}, f"<CipherMessage version {VERSION}, symmetric GCM_AEAD mode, 128 bit, len: 0 bytes>"),
        (
            {"key_size": 24},
            f"<CipherMessage version {VERSION}, symmetric GCM_AEAD mode, 192 bit, len: 0 bytes>",
        ),
        (
            {"key_size": 32},
            f"<CipherMessage version {VERSION}, symmetric GCM_AEAD mode, 256 bit, len: 0 bytes>",
        ),
        (
            {"cipher_text": "yo!"},
            f"<CipherMessage version {VERSION}, symmetric GCM_AEAD mode, 128 bit, len: 3 bytes>",
        ),
    ],
)
def test_message_validation_valid_messages(valid_message, kwargs, _repr):
    message = valid_message.__dict__
    message.update(kwargs)
    cipherMessage = CipherMessage(**message)
    cipherMessage.validate()
    assert repr(cipherMessage) == _repr


@pytest.mark.parametrize(
    "kwargs,exc",
    [
        ({"salt": "ssss".encode()}, "invalid salt"),
        ({"nonce": "nnnn".encode()}, "invalid nonce"),
        ({"mode": 255}, "bad cipher mode"),
        ({"version": 420}, "bad version number"),
        ({"key_size": 1}, "unsupported key size: 8 bit"),
    ],
)
def test_message_validation_invalid_messages(valid_message, kwargs, exc):
    with pytest.raises(ValueError, match=f"Not a valid ciphertext for this module: {exc}."):
        message = valid_message.__dict__
        message.update(kwargs)
        CipherMessage(**message).validate()
