import enum


class AESKeySize(int, enum.Enum):
    """Enumerates valid options for AES key sizes in bits, mapped to size in bytes used by the underlying libraries."""

    AES_128 = 16
    AES_192 = 24
    AES_256 = 32


class CipherMode(enum.IntFlag):
    """
    Enumerates valid and supported cipher modes.

    NOTE: Don't introduce more than 2^7 - 1 options for cipher modes, the MSB is for symmetric vs asymettric
    """

    GCM_AEAD = 1
    ASYMMETRIC = 0
    SYMMETRIC = 128


# Default key length
PBKDF2_KEY_LEN = 32
# Change any time recommendations change, previously encrypted data will still decrypt.
PBKDF2_ITERATIONS = 320000
VERSION = 0x02
SUPPORTED_VERSIONS = (VERSION,)
# Nothing is done with this information except makes us a bit more sure the input data is valid and it allows us to
# add more modes if we will ever need them.
SUPPORTED_MODES = (CipherMode.GCM_AEAD | CipherMode.SYMMETRIC,)
