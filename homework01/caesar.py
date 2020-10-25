import typing as tp


def encrypt_caesar(plaintext: str, shift: int = 3) -> str:
    """
    Encrypts plaintext using a Caesar cipher.

    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""
    alph = [chr(letter) for letter in range((ord("z") - shift + 1), ord("z") + 1)]
    alph.extend([chr(letter) for letter in range((ord("Z") - shift + 1), ord("Z") + 1)])
    for letter in plaintext:
        if ("a" <= letter <= "z") or ("A" <= letter <= "Z"):
            if letter in alph:
                ciphertext = ciphertext + chr(ord(letter) - 26 + shift)
            else:
                ciphertext = ciphertext + chr(ord(letter) + shift)
        else:
            ciphertext += letter
    return ciphertext


def decrypt_caesar(ciphertext: str, shift: int = 3) -> str:
    """
    Decrypts a ciphertext using a Caesar cipher.

    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""
    alph = [chr(letter) for letter in range(ord("a"), (ord("a") + shift))]
    alph.extend([chr(letter) for letter in range(ord("A"), (ord("A") + shift))])
    for letter in ciphertext:
        if ("a" <= letter <= "z") or ("A" <= letter <= "Z"):
            if letter in alph:
                plaintext = plaintext + chr(ord(letter) + 26 - shift)
            else:
                plaintext = plaintext + chr(ord(letter) - shift)
        else:
            plaintext += letter
    return plaintext


def caesar_breaker_brute_force(ciphertext: str, dictionary: tp.Set[str]) -> int:
    """
    Brute force breaking a Caesar cipher.
    """
    best_shift = 0
    for i in range(26):
        if decrypt_caesar(ciphertext, i) in dictionary:
            best_shift = i
    return best_shift
