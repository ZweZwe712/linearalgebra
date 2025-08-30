import numpy as np
from utils.matrix_utils import matrix_mod_inv
import os

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?;:'\"-()[]{}<>@#$%^&*_+=/\\|`~"
modulus = len(alphabet)
letter_to_index = {ch: i for i, ch in enumerate(alphabet)}
index_to_letter = {i: ch for i, ch in enumerate(alphabet)}


def generate_key(n=3):
    """Generate a random invertible n×n matrix mod alphabet length."""
    while True:
        K = np.random.randint(0, modulus, size=(n, n))
        try:
            _ = matrix_mod_inv(K, modulus)
            return K
        except ValueError:
            continue  # try again until invertible


def encrypt(message, K):
    message_numbers = [letter_to_index[ch] for ch in message]

    # Pad automatically
    while len(message_numbers) % K.shape[0] != 0:
        message_numbers.append(letter_to_index[" "])

    ciphertext = ""
    for i in range(0, len(message_numbers), K.shape[0]):
        block = np.array(message_numbers[i:i+K.shape[0]])[:, np.newaxis]
        numbers = np.dot(K, block) % modulus
        ciphertext += "".join(index_to_letter[int(num.item())] for num in numbers)
    return ciphertext


def decrypt(cipher, Kinv):
    cipher_numbers = [letter_to_index[ch] for ch in cipher]
    
    decrypted = ""
    for i in range(0, len(cipher_numbers), Kinv.shape[0]):
        block = np.array(cipher_numbers[i:i+Kinv.shape[0]])[:, np.newaxis]

        # Auto-pad if last block is short
        while block.shape[0] < Kinv.shape[0]:
            block = np.vstack([block, [[letter_to_index[" "]]]])

        numbers = np.dot(Kinv, block) % modulus
        decrypted += "".join(index_to_letter[int(num)] for num in numbers)

    return decrypted.rstrip()  # remove padding at end


def run():
    print("\n--- Text Mode ---")
    while True:
        print("\nText Mode:")
        print("a. Encode")
        print("b. Decode")
        choice = input("Enter choice (a/b): ").lower()
        
        if choice == "a":
            msg = input("Enter your message to encode: ")
            filename = input("Base filename (e.g. message): ")

            # Generate random key and save
            K = generate_key(3)
            np.savetxt(f"{filename}.txt.key", K, fmt="%d")

            # Encrypt
            cipher = encrypt(msg, K)
            print(f"🔑 Encoded message: {cipher}")
            with open(f"{filename}-encoded.txt", "w", encoding="utf-8") as f:
                f.write(cipher)

            print(f"🔐 Encoded text saved to {filename}-encoded.txt")
            print(f"🔑 Key matrix saved to {filename}.txt.key")

        elif choice == "b":
            filename = input("Base filename used (e.g. message): ")

            # Load key
            if not os.path.exists(f"{filename}.txt.key"):
                print("❌ Key file not found!")
                continue

            K = np.loadtxt(f"{filename}.txt.key", dtype=int)
            Kinv = matrix_mod_inv(K, modulus)

            # Load cipher
            if not os.path.exists(f"{filename}-encoded.txt"):
                print("❌ Ciphertext file not found!")
                continue

            with open(f"{filename}-encoded.txt", "r", encoding="utf-8") as f:
                cipher = f.read()

            plain = decrypt(cipher, Kinv)
            print(f"🔑 Decoded message: {plain}")
            with open(f"{filename}-decoded.txt", "w", encoding="utf-8") as f:
                f.write(plain)

            print(f"🔐 Decoded text saved to {filename}-decoded.txt")

        else:
            print("Invalid choice for text mode.")