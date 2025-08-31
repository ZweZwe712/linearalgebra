import os
import numpy as np
from math import gcd
import imageio.v2 as imageio
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox


# ---------- Math helpers ----------
def mod_matrix_inv(matrix: np.ndarray, modulus: int) -> np.ndarray:
    """Modular inverse of a square integer matrix under given modulus."""
    n = matrix.shape[0]
    det_val = int(round(np.linalg.det(matrix))) % modulus
    if gcd(det_val, modulus) != 1:
        raise ValueError(f"Matrix determinant {det_val} not invertible mod {modulus}")
    det_inv = pow(det_val, -1, modulus)

    cofactors = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            minor = np.delete(np.delete(matrix, i, axis=0), j, axis=1)
            cofactors[i, j] = ((-1) ** (i + j)) * int(round(np.linalg.det(minor)))

    adj = (cofactors.T % modulus)
    return (det_inv * adj) % modulus


# ---------- Hill for byte streams ----------
class Hill:
    def __init__(self, key: np.ndarray | None = None, modulus: int = 256):
        self._key = np.array([[3, 3], [2, 5]], dtype=int) if key is None else np.array(key, dtype=int)
        self.modulus = modulus
        self.n = self._key.shape[0]
        self._inv = mod_matrix_inv(self._key, modulus)

    def _blocks(self, data: np.ndarray) -> tuple[np.ndarray, int]:
        flat = data.reshape(-1).astype(int)
        L = flat.size
        pad = (-L) % self.n
        if pad:
            flat = np.pad(flat, (0, pad), mode="constant")
            print(f"Padding applied: added {pad} zero(s) to match block size.")
        m = flat.size // self.n
        return flat.reshape(m, self.n).T, L

    def _unblocks(self, arr: np.ndarray, orig_len: int) -> np.ndarray:
        out = arr.T.reshape(-1)[:orig_len]
        return out.astype(np.uint8)

    def encode(self, data: np.ndarray, verbose=False) -> np.ndarray:
        B, L = self._blocks(data)
        encrypted_blocks = (self._key @ B) % self.modulus
        if verbose:
            for i in range(B.shape[1]):
                print(f"\nBlock {i+1}:")
                print("Input vector:\n", B[:, i])
                print("Key matrix:\n", self._key)
                print("Multiplication result:\n", (self._key @ B[:, i]))
                print("After mod", self.modulus, ":\n", encrypted_blocks[:, i])
        return self._unblocks(encrypted_blocks, L)

    def decode(self, data: np.ndarray, verbose=False) -> np.ndarray:
        B, L = self._blocks(data)
        decrypted_blocks = (self._inv @ B) % self.modulus
        if verbose:
            for i in range(B.shape[1]):
                print(f"\nBlock {i+1}:")
                print("Encrypted vector:\n", B[:, i])
                print("Inverse key matrix:\n", self._inv)
                print("Multiplication result:\n", (self._inv @ B[:, i]))
                print("After mod", self.modulus, ":\n", decrypted_blocks[:, i])
        return self._unblocks(decrypted_blocks, L)



# ---------- Shared helper ----------
def _show_image(label: tk.Label, path: str):
    img = Image.open(path).convert("RGB")
    img.thumbnail((260, 260))
    tkimg = ImageTk.PhotoImage(img)
    label.config(image=tkimg)
    label.image = tkimg


# ---------- GUI for encoding ----------
def run_encoder(parent: tk.Misc | None = None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("Image Encoder")

    lbl_original = tk.Label(window, text="Original", compound="top")
    lbl_original.pack(side="left", padx=8)
    lbl_encoded = tk.Label(window, text="Encoded", compound="top")
    lbl_encoded.pack(side="left", padx=8)

    key_entry = tk.Entry(window, width=24)
    key_entry.insert(0, "3,3;2,5")
    key_entry.pack(pady=6)

    state = {"path": None, "shape": None, "arr": None, "key": Hill()}

    def parse_key():
        try:
            rows = [[int(x) for x in r.split(",")] for r in key_entry.get().strip().split(";")]
            state["key"] = Hill(np.array(rows, dtype=int))
            return True
        except Exception as e:
            messagebox.showerror("Invalid key", str(e))
            return False

    def pick_image():
        path = filedialog.askopenfilename(parent=window, title="Select an Image")
        if not path: return
        pil = Image.open(path).convert("RGB")
        arr = np.array(pil, dtype=np.uint8)
        state.update({"path": path, "shape": arr.shape, "arr": arr})
        _show_image(lbl_original, path)

    def encrypt():
        if state["arr"] is None or not parse_key(): return
        enc = state["key"].encode(state["arr"].reshape(-1)).reshape(state["shape"])
        out_path = os.path.splitext(state["path"])[0] + "-encoded.png"
        imageio.imwrite(out_path, enc)
        _show_image(lbl_encoded, out_path)
        messagebox.showinfo("Saved", f"Encoded image saved:\n{out_path}")

    tk.Button(window, text="Load Image", command=pick_image).pack(pady=4)
    tk.Button(window, text="Encrypt", command=encrypt).pack(pady=4)

    if not parent:
        window.mainloop()


# ---------- GUI for decoding ----------
def run_decoder(parent: tk.Misc | None = None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("Image Decoder")

    lbl_encoded = tk.Label(window, text="Encoded", compound="top")
    lbl_encoded.pack(side="left", padx=8)
    lbl_decoded = tk.Label(window, text="Decoded", compound="top")
    lbl_decoded.pack(side="left", padx=8)

    key_entry = tk.Entry(window, width=24)
    key_entry.insert(0, "3,3;2,5")
    key_entry.pack(pady=6)

    state = {"path": None, "shape": None, "arr": None, "key": Hill()}

    def parse_key():
        try:
            rows = [[int(x) for x in r.split(",")] for r in key_entry.get().strip().split(";")]
            state["key"] = Hill(np.array(rows, dtype=int))
            return True
        except Exception as e:
            messagebox.showerror("Invalid key", str(e))
            return False

    def pick_image():
        path = filedialog.askopenfilename(parent=window, title="Select an Encoded Image")
        if not path: return
        pil = Image.open(path).convert("RGB")
        arr = np.array(pil, dtype=np.uint8)
        state.update({"path": path, "shape": arr.shape, "arr": arr})
        _show_image(lbl_encoded, path)

    def decrypt():
        if state["arr"] is None or not parse_key(): return
        dec = state["key"].decode(state["arr"].reshape(-1)).reshape(state["shape"])
        out_path = os.path.splitext(state["path"])[0] + "-decoded.png"
        imageio.imwrite(out_path, dec)
        _show_image(lbl_decoded, out_path)
        messagebox.showinfo("Saved", f"Decoded image saved:\n{out_path}")

    tk.Button(window, text="Load Encoded Image", command=pick_image).pack(pady=4)
    tk.Button(window, text="Decrypt", command=decrypt).pack(pady=4)

    if not parent:
        window.mainloop()


if __name__ == "__main__":
    run_encoder()

