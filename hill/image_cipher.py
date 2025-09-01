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
    img.thumbnail((300, 300))
    tkimg = ImageTk.PhotoImage(img)
    label.config(image=tkimg)
    label.image = tkimg


def create_styled_button(parent, text, command, color, width=15):
    """Create a styled button with hover effects"""
    btn = tk.Button(parent, text=text, command=command,
                   font=('Segoe UI', 10, 'bold'),  # Slightly smaller font
                   bg=color, fg='white',
                   relief='flat', bd=0, cursor='hand2',
                   width=width, height=1,  # Reduced height from 2 to 1
                   pady=8)  # Added padding for better appearance
    
    # Color mapping for hover effects
    hover_colors = {
        '#2196f3': '#1976d2',
        '#4caf50': '#388e3c', 
        '#9c27b0': '#7b1fa2',
        '#f44336': '#d32f2f'
    }
    
    hover_color = hover_colors.get(color, color)
    
    def on_enter(e):
        btn.configure(bg=hover_color)
    
    def on_leave(e):
        btn.configure(bg=color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


# ---------- GUI for encoding ----------
def run_encoder(parent: tk.Misc | None = None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("🖼️ Image Encoder - Hill Cipher")
    window.geometry("1000x750")  # Increased height
    window.minsize(800, 600)  # Set minimum size
    window.configure(bg='#1a1a2e')
    
    # Center the window
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (1000 // 2)
    y = (window.winfo_screenheight() // 2) - (750 // 2)
    window.geometry(f"1000x750+{x}+{y}")
    
    # Header - reduced padding
    header_frame = tk.Frame(window, bg='#1a1a2e')
    header_frame.pack(pady=15)  # Reduced from 20
    
    title_label = tk.Label(header_frame, text="🖼️ IMAGE ENCODER",
                          font=('Segoe UI', 22, 'bold'),  # Slightly smaller
                          fg='#64b5f6', bg='#1a1a2e')
    title_label.pack()
    
    subtitle_label = tk.Label(header_frame, text="Encrypt images using Hill Cipher algorithm",
                             font=('Segoe UI', 10),  # Slightly smaller
                             fg='#90a4ae', bg='#1a1a2e')
    subtitle_label.pack(pady=(5, 0))
    
    # Image display area - better space allocation
    image_frame = tk.Frame(window, bg='#1a1a2e')
    image_frame.pack(fill='both', expand=True, padx=30, pady=15)  # Reduced padding
    
    # Left panel - Original image
    left_panel = tk.Frame(image_frame, bg='#16213e', relief='flat', bd=2)
    left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
    
    tk.Label(left_panel, text="📁 Original Image",
             font=('Segoe UI', 11, 'bold'),  # Slightly smaller
             fg='white', bg='#16213e').pack(pady=8)  # Reduced padding
    
    lbl_original = tk.Label(left_panel, text="No image loaded",
                           font=('Segoe UI', 10),  # Smaller font
                           fg='#78909c', bg='#263238',
                           width=40, height=12,  # Reduced height
                           compound='center')
    lbl_original.pack(padx=15, pady=(0, 10), fill='both', expand=True)
    
    # Right panel - Encoded image  
    right_panel = tk.Frame(image_frame, bg='#16213e', relief='flat', bd=2)
    right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
    
    tk.Label(right_panel, text="🔐 Encoded Image",
             font=('Segoe UI', 11, 'bold'),
             fg='white', bg='#16213e').pack(pady=8)
    
    lbl_encoded = tk.Label(right_panel, text="Encrypted image will appear here",
                          font=('Segoe UI', 10),
                          fg='#78909c', bg='#263238',
                          width=40, height=12,
                          compound='center')
    lbl_encoded.pack(padx=15, pady=(0, 10), fill='both', expand=True)
    
    # Key input section - more compact
    key_frame = tk.Frame(window, bg='#16213e', relief='flat')
    key_frame.pack(fill='x', padx=30, pady=(0, 15))  # Reduced padding
    
    tk.Label(key_frame, text="🔑 Encryption Key Matrix:",
             font=('Segoe UI', 10, 'bold'),  # Smaller font
             fg='white', bg='#16213e').pack(pady=(10, 5))  # Reduced padding
    
    key_entry = tk.Entry(key_frame, width=30,
                        font=('Consolas', 9),  # Smaller font
                        bg='#263238', fg='white',
                        insertbackground='white',
                        justify='center')
    key_entry.insert(0, "3,3;2,5")
    key_entry.pack(pady=3)  # Reduced padding
    
    tk.Label(key_frame, text="💡 Format: row1val1,row1val2;row2val1,row2val2",
             font=('Segoe UI', 8),  # Smaller font
             fg='#78909c', bg='#16213e').pack(pady=(0, 10))  # Reduced padding

    # State management
    state = {"path": None, "shape": None, "arr": None, "key": Hill()}

    def parse_key():
        try:
            rows = [[int(x) for x in r.split(",")] for r in key_entry.get().strip().split(";")]
            state["key"] = Hill(np.array(rows, dtype=int))
            return True
        except Exception as e:
            messagebox.showerror("Invalid Key", f"Key format error:\n{str(e)}\n\nExpected format: 3,3;2,5")
            return False

    def pick_image():
        path = filedialog.askopenfilename(parent=window, title="Select an Image",
                                        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                                                 ("All files", "*.*")])
        if not path: 
            return
        try:
            pil = Image.open(path).convert("RGB")
            arr = np.array(pil, dtype=np.uint8)
            state.update({"path": path, "shape": arr.shape, "arr": arr})
            _show_image(lbl_original, path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def encrypt():
        if state["arr"] is None:
            messagebox.showwarning("No Image", "Please load an image first.")
            return
        if not parse_key(): 
            return
        try:
            enc = state["key"].encode(state["arr"].reshape(-1)).reshape(state["shape"])
            out_path = os.path.splitext(state["path"])[0] + "-encoded.png"
            imageio.imwrite(out_path, enc)
            _show_image(lbl_encoded, out_path)
            messagebox.showinfo("Success", f"Encoded image saved:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to encrypt image:\n{str(e)}")

    # Buttons - fixed positioning
    btn_frame = tk.Frame(window, bg='#1a1a2e')
    btn_frame.pack(side='bottom', pady=20, padx=30)  # Use side='bottom' for better positioning
    
    create_styled_button(btn_frame, "📂 Load Image", pick_image, '#2196f3').pack(side='left', padx=8)
    create_styled_button(btn_frame, "🔐 Encrypt Image", encrypt, '#4caf50').pack(side='left', padx=8)
    create_styled_button(btn_frame, "🚪 Exit", window.destroy, '#f44336').pack(side='left', padx=8)

    if not parent:
        window.mainloop()


# ---------- GUI for decoding ----------
def run_decoder(parent: tk.Misc | None = None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("🔍 Image Decoder - Hill Cipher")
    window.geometry("1000x750")  # Increased height
    window.minsize(800, 600)  # Set minimum size
    window.configure(bg='#1a1a2e')
    
    # Center the window
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (1000 // 2)
    y = (window.winfo_screenheight() // 2) - (750 // 2)
    window.geometry(f"1000x750+{x}+{y}")
    
    # Header - reduced padding
    header_frame = tk.Frame(window, bg='#1a1a2e')
    header_frame.pack(pady=15)  # Reduced from 20
    
    title_label = tk.Label(header_frame, text="🔍 IMAGE DECODER",
                          font=('Segoe UI', 22, 'bold'),  # Slightly smaller
                          fg='#64b5f6', bg='#1a1a2e')
    title_label.pack()
    
    subtitle_label = tk.Label(header_frame, text="Decrypt Hill Cipher encoded images",
                             font=('Segoe UI', 10),  # Slightly smaller
                             fg='#90a4ae', bg='#1a1a2e')
    subtitle_label.pack(pady=(5, 0))
    
    # Image display area - better space allocation
    image_frame = tk.Frame(window, bg='#1a1a2e')
    image_frame.pack(fill='both', expand=True, padx=30, pady=15)  # Reduced padding
    
    # Left panel - Encoded image
    left_panel = tk.Frame(image_frame, bg='#16213e', relief='flat', bd=2)
    left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
    
    tk.Label(left_panel, text="🔐 Encoded Image",
             font=('Segoe UI', 11, 'bold'),  # Slightly smaller
             fg='white', bg='#16213e').pack(pady=8)  # Reduced padding
    
    lbl_encoded = tk.Label(left_panel, text="No encoded image loaded",
                          font=('Segoe UI', 10),  # Smaller font
                          fg='#78909c', bg='#263238',
                          width=40, height=12,  # Reduced height
                          compound='center')
    lbl_encoded.pack(padx=15, pady=(0, 10), fill='both', expand=True)
    
    # Right panel - Decoded image
    right_panel = tk.Frame(image_frame, bg='#16213e', relief='flat', bd=2)
    right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
    
    tk.Label(right_panel, text="📁 Decoded Image",
             font=('Segoe UI', 11, 'bold'),
             fg='white', bg='#16213e').pack(pady=8)
    
    lbl_decoded = tk.Label(right_panel, text="Decrypted image will appear here",
                          font=('Segoe UI', 10),
                          fg='#78909c', bg='#263238',
                          width=40, height=12,
                          compound='center')
    lbl_decoded.pack(padx=15, pady=(0, 10), fill='both', expand=True)
    
    # Key input section - more compact
    key_frame = tk.Frame(window, bg='#16213e', relief='flat')
    key_frame.pack(fill='x', padx=30, pady=(0, 15))  # Reduced padding
    
    tk.Label(key_frame, text="🔑 Decryption Key Matrix:",
             font=('Segoe UI', 10, 'bold'),  # Smaller font
             fg='white', bg='#16213e').pack(pady=(10, 5))  # Reduced padding
    
    key_entry = tk.Entry(key_frame, width=30,
                        font=('Consolas', 9),  # Smaller font
                        bg='#263238', fg='white',
                        insertbackground='white',
                        justify='center')
    key_entry.insert(0, "3,3;2,5")
    key_entry.pack(pady=3)  # Reduced padding
    
    tk.Label(key_frame, text="💡 Format: row1val1,row1val2;row2val1,row2val2",
             font=('Segoe UI', 8),  # Smaller font
             fg='#78909c', bg='#16213e').pack(pady=(0, 10))  # Reduced padding

    # State management
    state = {"path": None, "shape": None, "arr": None, "key": Hill()}

    def parse_key():
        try:
            rows = [[int(x) for x in r.split(",")] for r in key_entry.get().strip().split(";")]
            state["key"] = Hill(np.array(rows, dtype=int))
            return True
        except Exception as e:
            messagebox.showerror("Invalid Key", f"Key format error:\n{str(e)}\n\nExpected format: 3,3;2,5")
            return False

    def pick_image():
        path = filedialog.askopenfilename(parent=window, title="Select an Encoded Image",
                                        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                                                 ("All files", "*.*")])
        if not path: 
            return
        try:
            pil = Image.open(path).convert("RGB")
            arr = np.array(pil, dtype=np.uint8)
            state.update({"path": path, "shape": arr.shape, "arr": arr})
            _show_image(lbl_encoded, path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image:\n{str(e)}")

    def decrypt():
        if state["arr"] is None:
            messagebox.showwarning("No Image", "Please load an encoded image first.")
            return
        if not parse_key(): 
            return
        try:
            dec = state["key"].decode(state["arr"].reshape(-1)).reshape(state["shape"])
            out_path = os.path.splitext(state["path"])[0] + "-decoded.png"
            imageio.imwrite(out_path, dec)
            _show_image(lbl_decoded, out_path)
            messagebox.showinfo("Success", f"Decoded image saved:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt image:\n{str(e)}")

    # Buttons - fixed positioning
    btn_frame = tk.Frame(window, bg='#1a1a2e')
    btn_frame.pack(side='bottom', pady=20, padx=30)  # Use side='bottom' for better positioning
    
    create_styled_button(btn_frame, "📂 Load Encoded Image", pick_image, '#2196f3', 18).pack(side='left', padx=8)
    create_styled_button(btn_frame, "🔓 Decrypt Image", decrypt, '#9c27b0').pack(side='left', padx=8)
    create_styled_button(btn_frame, "🚪 Exit", window.destroy, '#f44336').pack(side='left', padx=8)

    if not parent:
        window.mainloop()


if __name__ == "__main__":
    run_encoder()