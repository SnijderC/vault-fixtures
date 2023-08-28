"""
Simple symmetric encryption, encrypts and decrypts, signs and verifies data with just a password.

Uses AES-GCM-128-AEAD as a cipher and authentication mechanism, and PBKDF2HMAC for key derivation.

Deliberately kept simple: encrypts and decrypts strings and only returns strings without supporting any additional
binary formats etc. It tries to do 1 thing, and tries to do it well and tries to make it hard to screw it up.

Uses a binary format described in the message module.
"""

import os
from functools import lru_cache
from typing import Optional, Text

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from vault_fix._crypto.constants import PBKDF2_ITERATIONS, PBKDF2_KEY_LEN, AESKeySize, CipherMode
from vault_fix._crypto.message import CipherMessage


class SymmetricCrypto:
    """Symmetric encryption and decryption of strings."""

    def __init__(self, password: str):
        """
        Initialiase the simple crypto class with a password.

        :param password: This should be hard to guess, obviously.
        """
        self.password = password

    @lru_cache(1000)
    def _derive_key_from_password(
        self,
        password: str,
        salt: bytes,
        length: Optional[int] = None,
        iterations: Optional[int] = None,
    ) -> bytes:
        """
        Apply PBKDF2HMAC to the password and a salt to generate a secure key.

        :param password: This should be hard to guess, obviously.
        :param salt: Some random bytes to make it impossible to pre-generate hashed passwords.
        :param length: Override the length for key stretching.
        :param iterations: Override the amount of key stretching iterations [default=320000].
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length or PBKDF2_KEY_LEN,
            salt=salt,
            iterations=iterations or PBKDF2_ITERATIONS,
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: Text, key_size: AESKeySize = AESKeySize.AES_128) -> str:
        """
        Encrypts a byte-like object or string.

        :param data: Byte-like object or string to encrypt.
        :param keySize: Size of the cipher key.
        :return: Base64 encoded, encrypted data plus the PBKDF iterations, key size and salt in a binary format.
        """
        salt = os.urandom(16)
        key = self._derive_key_from_password(self.password, salt, key_size)
        message = CipherMessage(
            salt=salt,
            mode=CipherMode.GCM_AEAD | CipherMode.SYMMETRIC,
            pbkdf2_iterations=PBKDF2_ITERATIONS,
            key_size=key_size,
            nonce=os.urandom(12),
        )
        aesgcm = AESGCM(key)
        data_bytes = data.encode() if isinstance(data, str) else data
        message.cipher_text = aesgcm.encrypt(message.nonce, data_bytes, message.aad)
        return str(message)

    def decrypt(self, data: Text, encoding="utf-8") -> str:
        """
        Decrypt data encrypted by this class.

        Extracts the key size, key stretching iterations from the ciphertext and uses it together with the password
        to decrypt the data.

        :param data: Byte-like object or string to encrypt, should be previously encrypted by this class.
        :param encoding: Which encoding to use to return the decrypted bytes to a string.
        :raises ValueError: If the message can't be decrypted.
        :return: Decrypted string with chosen encoding applied.
        """
        message = CipherMessage.unpack(data)
        key = self._derive_key_from_password(self.password, message.salt, message.key_size, message.pbkdf2_iterations)
        message.validate()
        aesgcm = AESGCM(key)
        try:
            return aesgcm.decrypt(message.nonce, message.cipher_text, message.aad).decode(encoding)
        except InvalidTag:
            raise ValueError("Failed to decrypt, bad message or password.") from None
