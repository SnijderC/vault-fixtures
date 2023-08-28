"""
Defines a message wrapper for cipher text that can hold required metadata to decrypt the cipher text.

Uses a binary format containing some metadata needed to decrypt messages without requiring knowledge on the parameters
used to encrypt the string, the format is:

BASE64( VERSION + PBKDF2_ITERATIONS + KEYSIZE + CIPHERMODE + SALT    + NONCE  +  CIPHERTEXT )
        ^         ^                   ^         ^            ^         ^         ^
        2 bytes   4 bytes             1 byte    1 byte       16 bytes  12 bytes  n bytes
"""
import base64
import struct
from dataclasses import dataclass
from typing import Text

from vault_fix._crypto.constants import SUPPORTED_MODES, SUPPORTED_VERSIONS, VERSION, AESKeySize, CipherMode


@dataclass
class CipherMessage:
    """Wrapper for cipher messages."""

    salt: bytes
    mode: CipherMode
    pbkdf2_iterations: int
    key_size: int
    nonce: bytes
    version: int = VERSION
    cipher_text: bytes = b""

    @property
    def aad(self) -> bytes:
        """
        Packed used version, PBKDF2 iterations, cipher mode, key size and salt.

        NOTE::
            "aad" stands for Additional Authenticated Data some authenticated ciphers can add unencrypted data that
            **is** authenticated. It's used here to store authenticate the message meta data so it can't be messed
            with.
        """
        mode = self.key_size << 8 | self.mode.value
        return struct.pack("<HHI", VERSION, mode, self.pbkdf2_iterations) + self.salt + self.nonce

    @classmethod
    def unpack(cls, data: Text) -> "CipherMessage":
        """
        Unpacks data from a byte-like object or string and returns a CipherMessage.

        :param data: A byte-like object or string that contains the cipher message.
        :return: CipherMessage object with populated fields.
        """
        if len(data) < 36:
            raise ValueError("Not a valid ciphertext for this module: bad message.")
        decoded = base64.b64decode(data)
        aad = decoded[0:36]
        version, key_size_and_mode, pbkdf2_iterations, salt, nonce = struct.unpack("<HHI16s12s", aad)
        return cls(
            version=version,
            mode=CipherMode(key_size_and_mode & 0x00FF),
            key_size=key_size_and_mode >> 8,
            pbkdf2_iterations=pbkdf2_iterations,
            salt=salt,
            nonce=nonce,
            cipher_text=decoded[36:],
        )

    def validate(self):
        """
        Validate that the message is valid and compatible with this version.

        :raises ValueError: If the data is badly formatted (very limited checking), or not supported.
        """
        if self.version not in SUPPORTED_VERSIONS:
            raise ValueError("Not a valid ciphertext for this module: bad version number.")
        if self.mode not in SUPPORTED_MODES:
            raise ValueError("Not a valid ciphertext for this module: bad cipher mode.")
        if len(self.salt) != 16:
            raise ValueError("Not a valid ciphertext for this module: invalid salt.")
        if len(self.nonce) != 12:
            raise ValueError("Not a valid ciphertext for this module: invalid nonce.")
        try:
            AESKeySize(self.key_size)
        except ValueError:
            raise ValueError(
                f"Not a valid ciphertext for this module: unsupported key size: {self.key_size*8} bit."
            ) from None

    def pack(self):
        """
        Add the meta data and salt before base64 encoding the result.

        :param encoding: Encoding to use to encode to a string input to bytes, ignored if input is not a string.
        """
        return base64.b64encode(self.aad + self.cipher_text).decode()

    def __repr__(self):
        """Generate a useful representation of the message."""
        cls = self.__class__.__name__
        length = len(self.cipher_text)
        mode = self.mode & ~CipherMode.SYMMETRIC
        symmetric = (self.mode & ~mode).name.lower()
        return (
            f"<{cls} version {self.version}, {symmetric} {str(mode.name)} mode, {self.key_size*8} bit,"
            f" len: {length} bytes>"
        )

    def __str__(self):
        return self.pack()
