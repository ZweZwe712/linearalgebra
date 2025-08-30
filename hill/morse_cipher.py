import numpy as np
from utils.matrix_utils import matrix_mod_inv
from utils.morse_utils import text_to_morse, morse_to_text

# Morse symbol alphabet and mappings
MORSE_ALPHABET = ".- /"  # dot, dash, space (letter sep), slash (word sep)
SYM_TO_IDX = {ch: i for i, ch in enumerate(MORSE_ALPHABET)}
IDX_TO_SYM = {i: ch for i, ch in enumerate(MORSE_ALPHABET)}
M = len(MORSE_ALPHABET)


def morse_hill_encrypt(morse: str, key_matrix: np.ndarray) -> str:
    n = key_matrix.shape[0]
    key_mod = key_matrix % M

    indices = [SYM_TO_IDX.get(ch, SYM_TO_IDX[' ']) for ch in morse]
    while len(indices) % n != 0:
        indices.append(SYM_TO_IDX[' '])

    blocks = np.array(indices, dtype=int).reshape(-1, n)
    enc = (blocks @ key_mod) % M
    enc_flat = enc.flatten().tolist()
    return "".join(IDX_TO_SYM[i] for i in enc_flat)


def morse_hill_decrypt(cipher: str, key_matrix: np.ndarray) -> str:
    n = key_matrix.shape[0]

    indices = [SYM_TO_IDX.get(ch, SYM_TO_IDX[' ']) for ch in cipher]
    while len(indices) % n != 0:
        indices.append(SYM_TO_IDX[' '])

    blocks = np.array(indices, dtype=int).reshape(-1, n)
    inv_matrix = matrix_mod_inv(key_matrix, M) % M
    dec = (blocks @ inv_matrix) % M
    dec_flat = dec.flatten().tolist()
    return "".join(IDX_TO_SYM[i] for i in dec_flat).rstrip()


def run():
    print("\n--- Morse-Cipher Mode ---")
    print("1. Text -> Morse")
    print("2. Morse -> Text")
    print("3. Encrypt Morse (Hill over .- /)")
    print("4. Decrypt Morse (Hill over .- /)")
    choice = input("Choose option: ")

    # 2x2 example key; works mod 4 since det=9≡1 (invertible)
    key = np.array([[3, 3], [2, 5]], dtype=int)

    if choice == "1":
        msg = input("Enter text message: ")
        morse = text_to_morse(msg)
        print("Morse code:", morse)

    elif choice == "2":
        morse = input("Enter morse code (use '.' '-' ' ' '/' ): ")
        text = morse_to_text(morse)
        print("Decoded text:", text)

    elif choice == "3":
        msg = input("Enter text message: ")
        morse = text_to_morse(msg)
        enc = morse_hill_encrypt(morse, key)
        print("Encrypted Morse:", enc)

    elif choice == "4":
        cipher = input("Enter encrypted morse: ")
        dec_morse = morse_hill_decrypt(cipher, key)
        print("Decrypted Morse:", dec_morse)
        text = morse_to_text(dec_morse)
        print("Decoded text:", text)

    else:
        print("Invalid option")