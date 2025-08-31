from typing import Self
import numpy as np
import tkinter as tk
from tkinter import messagebox, scrolledtext

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?;:'\"-()[]{}<>@#$%^&*_+=/\\|`~"
letter_to_index = {ch: i for i, ch in enumerate(alphabet)}
index_to_letter = {i: ch for i, ch in enumerate(alphabet)}
modulus = len(alphabet)


# ---------- Math helpers ----------
def mod_inv(a, m):
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError("No modular inverse")


def matrix_mod_inv(K, m):
    det = int(round(np.linalg.det(K)))
    det_inv = mod_inv(det, m)
    K_adj = np.round(det * np.linalg.inv(K)).astype(int) % m
    return (det_inv * K_adj) % m


def generate_key(n=3):
    while True:
        K = np.random.randint(0, modulus, size=(n, n))
        try:
            _ = matrix_mod_inv(K, modulus)
            return K
        except ValueError:
            continue


# ---------- Cipher ----------
def encrypt(message, K):
    message_numbers = [letter_to_index[ch] for ch in message if ch in letter_to_index]

    while len(message_numbers) % K.shape[0] != 0:
        message_numbers.append(letter_to_index[" "])

    ciphertext = ""
    for i in range(0, len(message_numbers), K.shape[0]):
        block = np.array(message_numbers[i:i+K.shape[0]])[:, np.newaxis]
        numbers = np.dot(K, block) % modulus
        ciphertext += "".join(index_to_letter[int(num.item())] for num in numbers)
    return ciphertext



def decrypt(cipher, Kinv):
    cipher_numbers = [letter_to_index[ch] for ch in cipher if ch in letter_to_index]

    decrypted = ""
    for i in range(0, len(cipher_numbers), Kinv.shape[0]):
        block = np.array(cipher_numbers[i:i+Kinv.shape[0]])[:, np.newaxis]

        while block.shape[0] < Kinv.shape[0]:
            block = np.vstack([block, [[letter_to_index[" "]]]])

        numbers = np.dot(Kinv, block) % modulus
        decrypted += "".join(index_to_letter[int(num)] for num in numbers)

    return decrypted.rstrip()


# ---------- GUI ----------


##--------------------------------------Proof OF Concept -----------------------------------------------
def encrypt_text(message, key_matrix, verbose=False):
    import numpy as np

    nums = [ord(c) - 65 for c in message.upper()]
    chunk_size = key_matrix.shape[0]
    chunks = [nums[i:i+chunk_size] for i in range(0, len(nums), chunk_size)]

    encrypted_chunks = []
    for chunk in chunks:
        # Pad with 'X' (23) if chunk is too short
        while len(chunk) < chunk_size:
            chunk.append(23)

        vec = np.array(chunk)
        if verbose:
            print("\nChunk vector:\n", vec)
            print("Key matrix:\n", key_matrix)
            print("Multiplication result:\n", np.dot(key_matrix, vec))

        enc_vec = np.dot(key_matrix, vec) % 26
        if verbose:
            print("After mod 26:\n", enc_vec)

        encrypted_chunks.extend(enc_vec)

    encrypted_text = ''.join(chr(int(num) + 65) for num in encrypted_chunks)
    return encrypted_text



# ---------------- GUI run (same structure as before, using the new functions) ----------------

def run(parent=None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("Text Cipher (Encrypt & Decrypt)")

    # Message for encryption
    tk.Label(window, text="Message (for Encryption):").pack(pady=4)
    msg_box = scrolledtext.ScrolledText(window, width=60, height=5)
    msg_box.pack(pady=4)

    # Ciphertext for decryption
    tk.Label(window, text="Ciphertext (for Decryption):").pack(pady=4)
    cipher_box = scrolledtext.ScrolledText(window, width=60, height=5)
    cipher_box.pack(pady=4)

    # Key input for decryption
    tk.Label(window, text="Key Matrix (rows separated by ';', values by ',')").pack(pady=4)
    key_box = scrolledtext.ScrolledText(window, width=60, height=4)
    key_box.pack(pady=4)

    # Buttons row for key copy/paste
    key_btns = tk.Frame(window)
    key_btns.pack(pady=2)
    tk.Button(key_btns, text="Copy Key", command=lambda: window.clipboard_append(key_box.get("1.0", tk.END).strip())).pack(side="left", padx=4)
    tk.Button(key_btns, text="Paste Key", command=lambda: (key_box.delete("1.0", tk.END), key_box.insert("1.0", window.clipboard_get()))).pack(side="left", padx=4)

    # Output
    tk.Label(window, text="Output:").pack(pady=4)
    out_box = scrolledtext.ScrolledText(window, width=60, height=8)
    out_box.pack(pady=4)

    def encrypt_message():
        msg = msg_box.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showerror("Error", "Enter a message to encrypt")
            return
        K = generate_key(3)
        cipher = encrypt(msg, K)

        # Format key for copy-paste
        key_str = ";".join(",".join(str(x) for x in row) for row in K)

        out_box.delete("1.0", tk.END)
        out_box.insert(tk.END, f"Ciphertext:\n{cipher}\n\nKey:\n{key_str}")

        cipher_box.delete("1.0", tk.END)
        cipher_box.insert(tk.END, cipher)
        key_box.delete("1.0", tk.END)
        key_box.insert(tk.END, key_str)

    def decrypt_message():
        cipher = cipher_box.get("1.0", tk.END).strip()
        key_str = key_box.get("1.0", tk.END).strip()

        if not cipher or not key_str:
            messagebox.showerror("Error", "Enter ciphertext and key")
            return

        try:
            rows = [[int(x) for x in r.split(",")] for r in key_str.split(";")]
            K = np.array(rows, dtype=int)
            Kinv = matrix_mod_inv(K, modulus)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid key format:\n{e}")
            return

        plain = decrypt(cipher, Kinv)
        out_box.delete("1.0", tk.END)
        out_box.insert(tk.END, f"Plaintext:\n{plain}")

    def back_to_main():
        """Close the current window and return to main menu."""
        window.destroy()

    # Buttons
    tk.Button(window, text="Encrypt", command=encrypt_message).pack(pady=6)
    tk.Button(window, text="Decrypt", command=decrypt_message).pack(pady=6)
    tk.Button(window, text="    Exit    ", command=back_to_main).pack(pady=6)

    if not parent:
        window.mainloop()


if __name__ == "__main__":
    run()

