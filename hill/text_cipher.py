import numpy as np
from utils.matrix_utils import matrix_mod_inv

def hill_encrypt(message, key_matrix):
    """Encrypt text using Hill cipher (mod 26)."""
    message = message.upper().replace(" ", "")
    n = key_matrix.shape[0]

    # pad message
    while len(message) % n != 0:
        message += "X"

    numbers = [ord(c) - ord('A') for c in message]
    numbers = np.array(numbers).reshape(-1, n)

    encrypted = (numbers @ key_matrix) % 26
    return "".join(chr(int(num) + ord('A')) for row in encrypted for num in row)

def hill_decrypt(cipher, key_matrix):
    """Decrypt text using Hill cipher (mod 26)."""
    n = key_matrix.shape[0]
    numbers = [ord(c) - ord('A') for c in cipher]
    numbers = np.array(numbers).reshape(-1, n)

    inv_matrix = matrix_mod_inv(key_matrix, 26)
    decrypted = (numbers @ inv_matrix) % 26
    return "".join(chr(int(num) + ord('A')) for row in decrypted for num in row)

def run():
    print("\n--- Text Mode ---")
    key = np.array([[3, 3], [2, 5]])  # Example 2x2 key
    msg = input("Enter a message: ")

    enc = hill_encrypt(msg, key)
    print("Encrypted:", enc)

    dec = hill_decrypt(enc, key)
    print("Decrypted:", dec)
