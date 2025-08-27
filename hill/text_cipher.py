import tkinter as tk
from tkinter import messagebox
import numpy as np
from utils.matrix_utils import matrix_mod_inv

# ---------------- Helper to collect letters and positions ----------------
def _collect_letters(text):
    """
    Return (letters_upper, letter_positions, original_cases)
      - letters_upper: list of uppercase letters (A..Z) from the text, in order
      - letter_positions: indices in original text where letters occur
      - original_cases: list of booleans parallel to letters indicating original was lowercase (True) or uppercase (False)
    """
    letters = []
    positions = []
    cases = []
    for i, ch in enumerate(text):
        if ch.isalpha():
            positions.append(i)
            cases.append(ch.islower())
            letters.append(ch.upper())
    return letters, positions, cases

# ---------------- Hill encrypt/decrypt preserving case & non-letters ----------------
def hill_encrypt(message, key_matrix):
    """Encrypt while preserving case and non-letters.
       - Letters are processed; other characters are kept in place.
       - If padding is required, extra cipher letters are appended at the end.
    """
    if key_matrix.shape[0] != key_matrix.shape[1]:
        raise ValueError("Key matrix must be square (n x n).")

    n = key_matrix.shape[0]
    letters, positions, cases = _collect_letters(message)

    # pad letters so length is multiple of n
    pad_count = (-len(letters)) % n
    if pad_count:
        letters += ['X'] * pad_count

    # numeric transform: A->0 .. Z->25
    nums = np.array([ord(c) - ord('A') for c in letters]).reshape(-1, n)
    encrypted = (nums @ key_matrix) % 26
    encrypted_flat = [chr(int(num) + ord('A')) for row in encrypted for num in row]

    # Build output: replace letters in original positions with encrypted letters preserving original case,
    # then append any remaining encrypted letters (from padding) to the end.
    out_chars = list(message)
    j = 0
    for pos_index, is_lower in zip(positions, cases):
        enc_ch = encrypted_flat[j]
        out_chars[pos_index] = enc_ch.lower() if is_lower else enc_ch
        j += 1

    # remaining encrypted letters (due to padding) append to end
    remaining = encrypted_flat[j:]
    if remaining:
        out_chars.extend(remaining)   # appended as uppercase (you may .lower() them if you prefer)
    return ''.join(out_chars)

def hill_decrypt(ciphertext, key_matrix, strip_padding=False):
    """Decrypt while preserving case/non-letters.
       - If strip_padding=True, trailing 'X' or 'x' characters that look like padding are stripped.
    """
    if key_matrix.shape[0] != key_matrix.shape[1]:
        raise ValueError("Key matrix must be square (n x n).")
    n = key_matrix.shape[0]

    letters, positions, cases = _collect_letters(ciphertext)
    if len(letters) % n != 0:
        raise ValueError(f"Cipher letter count ({len(letters)}) is not a multiple of key size ({n}).")

    nums = np.array([ord(c) - ord('A') for c in letters]).reshape(-1, n)
    inv_mat = matrix_mod_inv(key_matrix, 26)
    decrypted = (nums @ inv_mat) % 26
    decrypted_flat = [chr(int(num) + ord('A')) for row in decrypted for num in row]

    # Reinsert decrypted letters into original positions, using the *ciphertext's* case pattern
    out_chars = list(ciphertext)
    j = 0
    for pos_index in positions:
        dec_ch = decrypted_flat[j]
        out_chars[pos_index] = dec_ch.lower() if cases[j] else dec_ch
        j += 1

    result = ''.join(out_chars)
    if strip_padding:
        # Heuristic: remove trailing X/x characters (only if you accept the risk of removing a real trailing 'x')
        result = result.rstrip('Xx')
    return result

# ---------------- GUI run (same structure as before, using the new functions) ----------------
def run(parent=None):
    if parent is None:
        root = tk.Tk()
    else:
        root = tk.Toplevel(parent)
    root.title("Text Cipher (case-preserving)")

    tk.Label(root, text="Enter Text:").pack(pady=5)
    text_input = tk.Text(root, height=5, width=50)
    text_input.pack(pady=5)

    tk.Label(root, text="Key Matrix (rows separated by ;, numbers by ,):").pack(pady=5)
    key_entry = tk.Entry(root, width=50)
    key_entry.insert(0, "3,3;2,5")
    key_entry.pack(pady=5)

    result_box = tk.Text(root, height=6, width=50, bg="#f0f0f0")
    result_box.pack(pady=10)

    def parse_key():
        try:
            mat = np.array([list(map(int, r.split(","))) for r in key_entry.get().split(";")])
            if mat.shape[0] != mat.shape[1]:
                messagebox.showerror("Error", "Key matrix must be square (n x n).")
                return None
            return mat
        except Exception as e:
            messagebox.showerror("Invalid key", f"Key parse error: {e}")
            return None

    def on_encrypt():
        mat = parse_key()
        if mat is None: return
        msg = text_input.get("1.0", "end-1c")
        try:
            out = hill_encrypt(msg, mat)
        except Exception as e:
            messagebox.showerror("Encryption error", str(e))
            return
        result_box.delete("1.0", "end")
        result_box.insert("end", out)

    def on_decrypt():
        mat = parse_key()
        if mat is None: return
        msg = text_input.get("1.0", "end-1c")
        try:
            out = hill_decrypt(msg, mat, strip_padding=False)
        except Exception as e:
            messagebox.showerror("Decryption error", str(e))
            return
        result_box.delete("1.0", "end")
        result_box.insert("end", out)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=8)
    tk.Button(btn_frame, text="Encrypt", command=on_encrypt).pack(side="left", padx=12)
    tk.Button(btn_frame, text="Decrypt", command=on_decrypt).pack(side="left", padx=12)

    if parent is None:
        root.mainloop()

