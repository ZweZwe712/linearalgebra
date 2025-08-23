import numpy as np

# Alphabet
# alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz "
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?;:'\"-()[]{}<>@#$%^&*_+=/\\|`~"

letter_to_index = {ch: i for i, ch in enumerate(alphabet)}
index_to_letter = {i: ch for i, ch in enumerate(alphabet)}

# Example key matrix (3x3, must be invertible mod len(alphabet))
K = np.array([[6, 24, 1],
              [13, 16, 10],
              [20, 17, 15]])

modulus = len(alphabet)

# Modular inverse of determinant
def mod_inv(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError("No modular inverse")

# Inverse of key matrix mod m
def matrix_mod_inv(K, m):
    det = int(round(np.linalg.det(K)))  # determinant
    det_inv = mod_inv(det, m)           # modular inverse of determinant
    K_adj = np.round(det * np.linalg.inv(K)).astype(int) % m  # adjugate
    return (det_inv * K_adj) % m

Kinv = matrix_mod_inv(K, modulus)

# Encrypt
def encrypt(message, K):
    message_numbers = [letter_to_index[ch] for ch in message]

    # Pad automatically
    while len(message_numbers) % K.shape[0] != 0:
        message_numbers.append(letter_to_index[" "])

    ciphertext = ""
    for i in range(0, len(message_numbers), K.shape[0]):
        block = np.array(message_numbers[i:i+K.shape[0]])[:, np.newaxis]
        numbers = np.dot(K, block) % modulus
        # ciphertext += "".join(index_to_letter[int(num)] for num in numbers)
        ciphertext += "".join(index_to_letter[int(num.item())] for num in numbers)
    return ciphertext

# Decrypt
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

# Main loop
def main():
    while True:
        choice = input("Do you want to (e)ncrypt, (d)ecrypt, or e(x)it? ").lower()
        if choice == "e":
            msg = input("Enter your message to encrypt: ")
            print("🔐 Encrypted message:", encrypt(msg, K))
        elif choice == "d":
            msg = input("Enter your message to decrypt: ")
            print("🔑 Decrypted message:", decrypt(msg, Kinv))
        elif choice == "x":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter e, d, or x.")

if __name__ == "__main__":
    main()
