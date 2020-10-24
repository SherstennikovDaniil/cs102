def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    for i in range(len(plaintext)):
        key_pos = i % len(keyword)
        if ord('A') <= ord(keyword[key_pos]) <= ord('Z'):
            shift = ord(keyword[key_pos]) - ord('A')
        elif ord('a') <= ord(keyword[key_pos]) <= ord('z'):
            shift = ord(keyword[key_pos]) - ord('a')
        else:
            continue
        if ord('A') <= ord(plaintext[i]) <= ord('Z'):
            if ord('Z') - ord(plaintext[i]) < shift:
                ciphertext += chr(ord('A') - 1 + (shift - ord('Z') + ord(plaintext[i])))
            else:
                ciphertext += chr(ord(plaintext[i]) + shift)
        elif ord('a') <= ord(plaintext[i]) <= ord('z'):
            if ord('z') - ord(plaintext[i]) < shift:
                ciphertext += chr(ord('a') - 1 + (shift - ord('z') + ord(plaintext[i])))
            else:
                ciphertext += chr(ord(plaintext[i]) + shift)
        else:
            ciphertext += plaintext[i]
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    for i in range(len(ciphertext)):
        key_pos = i % len(keyword)
        if ord('A') <= ord(keyword[key_pos]) <= ord('Z'):
            shift = ord(keyword[key_pos]) - ord('A')
        elif ord('a') <= ord(keyword[key_pos]) <= ord('z'):
            shift = ord(keyword[key_pos]) - ord('a')
        else:
            continue
        if ord('A') <= ord(ciphertext[i]) <= ord('Z'):
            if ord(ciphertext[i]) - shift < ord('A'):
                plaintext += chr(ord('Z') + 1 - (shift - (ord(ciphertext[i]) - ord('A'))))
            else:
                plaintext += chr(ord(ciphertext[i]) - shift)
        elif ord('a') <= ord(ciphertext[i]) <= ord('z'):
            if ord(ciphertext[i]) - shift < ord('a'):
                plaintext += chr(ord('z') + 1 - (shift - (ord(ciphertext[i]) - ord('a'))))
            else:
                plaintext += chr(ord(ciphertext[i]) - shift)
        else:
            plaintext += ciphertext[i]
    return plaintext
