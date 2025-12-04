import hashlib
from Crypto.Hash import keccak


def keccak256(b: bytes) -> bytes:
    h = keccak.new(digest_bits=256)
    h.update(b)
    return h.digest()


def sha256(b: bytes) -> bytes:
    h = hashlib.new("sha256")
    h.update(b)
    return h.digest()