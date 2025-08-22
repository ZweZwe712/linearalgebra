import numpy as np
from scipy.io import wavfile
from utils.matrix_utils import matrix_mod_inv
from utils.morse_utils import text_to_morse, morse_to_text

def encrypt_audio(path, key_matrix):
    rate, data = wavfile.read(path)
    flat = data.flatten()
    n = key_matrix.shape[0]

    while len(flat) % n != 0:
        flat = np.append(flat, 0)

    flat = flat.reshape(-1, n)
    encrypted = (flat @ key_matrix) % 65536  # 16-bit audio range
    encrypted = encrypted.flatten()[:len(data)].astype(np.int16)

    wavfile.write("encrypted.wav", rate, encrypted)
    print("Saved encrypted.wav")

def decrypt_audio(path, key_matrix):
    rate, data = wavfile.read(path)
    flat = data.flatten()
    n = key_matrix.shape[0]

    flat = flat.reshape(-1, n)
    inv_matrix = matrix_mod_inv(key_matrix, 65536)
    decrypted = (flat @ inv_matrix) % 65536
    decrypted = decrypted.flatten()[:len(data)].astype(np.int16)

    wavfile.write("decrypted.wav", rate, decrypted)
    print("Saved decrypted.wav")

def run():
    print("\n--- Audio Mode ---")
    print("1. Normal WAV encryption")
    print("2. Morse Code encryption (text -> morse)")
    choice = input("Choose option: ")

    key = np.array([[3, 3], [2, 5]])  # Example key

    if choice == "1":
        path = input("Enter WAV file name: ")
        enc_or_dec = input("Encrypt or Decrypt? (e/d): ").lower()
        if enc_or_dec == "e":
            encrypt_audio(path, key)
        else:
            decrypt_audio(path, key)

    elif choice == "2":
        msg = input("Enter text message: ")
        morse = text_to_morse(msg)
        print("Morse code:", morse)

        # For now we’ll just encrypt/decrypt the Morse string as text
        from hill.text_cipher import hill_encrypt, hill_decrypt
        enc = hill_encrypt(morse.replace(" ", ""), key)
        dec = hill_decrypt(enc, key)
        print("Encrypted Morse:", enc)
        print("Decrypted Morse:", dec)

    else:
        print("Invalid option")
