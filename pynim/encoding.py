BASE58_ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58(b: bytes) -> bytes:
    num = int.from_bytes(b, byteorder='big')
    encoded = bytearray()
    while num > 0:
        num, rem = divmod(num, 58)
        encoded.insert(0, BASE58_ALPHABET[rem])
    leading_zeroes = len(b) - len(b.lstrip(b'\x00'))
    return BASE58_ALPHABET[0:1] * leading_zeroes + encoded