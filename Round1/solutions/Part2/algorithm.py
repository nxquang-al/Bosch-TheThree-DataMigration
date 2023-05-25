from hashlib import sha256

B = 64  # sha256 input block size
L = 32  # sha256 output block size
ipad = b'\x36' * B  # inner padding
opad = b'\x5c' * B  # outer padding


def H(s: bytes) -> bytes:
    """
    Compute the SHA256 hash of the given string.

    Args:
        s: The string to hash.

    Returns:
        The SHA256 hash of the given string.
    """
    return sha256(s).digest()


def pad(s: bytes, size: int = B) -> bytes:
    """
    Pad the given string with null bytes to the given size.

    Args:
        s: The string to pad.
        size: The size to pad to.

    Returns:
        The padded string.
    """
    return s + b'\x00' * (size - len(s))


def xor(s1: bytes, s2: bytes) -> bytes:
    """
    Compute the XOR of the given strings.

    Args:
        s1: The first string.
        s2: The second string.

    Returns:
        The XOR of the given strings.
    """
    return bytes(b1 ^ b2 for b1, b2 in zip(s1, s2))


def get_key(K: bytes) -> bytes:
    """
    Get the key to use for algorithm.

    Args:
        K: The key.

    Returns:
        The key to use for algorithm.
    """
    return pad(H(K) if len(K) > B else K)


def encrypt(K: bytes, text: bytes) -> bytes:
    """
    Encrypt the given text using the given key.

    Args:
        K: The key.
        text: The text to encrypt.

    Returns:
        The encrypted text.
    """
    K_0 = get_key(K)

    s4 = xor(K_0, ipad)
    s5 = s4 + text
    s6 = H(s5)
    s7 = xor(K_0, opad)
    s8 = s7 + s6
    s9 = H(s8)
    return s9


if __name__ == '__main__':
    K = input("Enter key: ")
    text = input("Enter text: ")
    # K = '0b' * 32
    # text = '4869205468657265'

    encrypted = encrypt(bytes.fromhex(K), bytes.fromhex(text))
    print("Encrypted string: ", encrypted.hex())
