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
    alph = [chr(letter) for letter in range((ord("z") - shift), ord("z"))] + [chr(letter) for letter in
                                                                              range((ord("Z") - shift), ord("Z"))]
    for letter in plaintext:
        if (ord("a") <= ord(letter) <= ord("z")) or (ord("A") <= ord(letter) <= ord("Z")):
            if letter in alph:
                ciphertext += chr(ord(letter) - 26 + shift)
            else:
                ciphertext += chr(ord(letter) + shift)
        else:
            plaintext += letter
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
    alph = [chr(letter) for letter in range(ord("a"), (ord("a") + shift))] + [chr(letter) for letter in
                                                                              range(ord("A"), (ord("A") + shift))]
    for letter in ciphertext:
        if (ord("a") <= ord(letter) <= ord("z")) or (ord("A") <= ord(letter) <= ord("Z")):
            if letter in alph:
                plaintext += chr(ord(letter) + 26 - shift)
            else:
                plaintext += chr(ord(letter) - shift)
        else:
            plaintext += letter
    return plaintext


def caesar_breaker_brute_force(ciphertext: str, dictionary: tp.Set[str]) -> int:
    """
    Brute force breaking a Caesar cipher.
    """
    best_shift = 0
    chars = ciphertext.split()
    for char in chars:
        for i in range(0, 26):
            dword = decrypt_caesar(char, i)
            if dword in dictionary:
                best_shift = i
    return best_shift