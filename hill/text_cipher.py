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


def create_styled_button(parent, text, command, color, width=15):
    """Create a styled button with hover effects"""
    btn = tk.Button(parent, text=text, command=command,
                   font=('Segoe UI', 11, 'bold'),
                   bg=color, fg='white',
                   relief='flat', bd=0, cursor='hand2',
                   width=width, height=2)
    
    # Color mapping for hover effects
    hover_colors = {
        '#4caf50': '#388e3c',
        '#ff9800': '#f57c00', 
        '#9e9e9e': '#757575',
        '#f44336': '#d32f2f',
        '#2196f3': '#1976d2'
    }
    
    hover_color = hover_colors.get(color, color)
    
    def on_enter(e):
        btn.configure(bg=hover_color)
    
    def on_leave(e):
        btn.configure(bg=color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn


# ---------- GUI ----------
def run(parent=None):
    window = tk.Toplevel(parent) if parent else tk.Tk()
    window.title("📝 Text Cipher - Hill Encryption Suite")
    window.geometry("1100x800")
    window.configure(bg='#1a1a2e')
    window.minsize(900, 600)
    
    # Center the window
    window.update_idletasks()
    x = (window.winfo_screenwidth() // 2) - (1100 // 2)
    y = (window.winfo_screenheight() // 2) - (800 // 2)
    window.geometry(f"1100x800+{x}+{y}")
    
    # Configure main window grid - 5 rows total
    window.grid_rowconfigure(2, weight=1)  # Content area expandable
    window.grid_columnconfigure(0, weight=1)
    
    # ROW 0: Header
    header_frame = tk.Frame(window, bg='#1a1a2e')
    header_frame.grid(row=0, column=0, sticky='ew', pady=20, padx=20)
    header_frame.grid_columnconfigure(0, weight=1)
    
    title_label = tk.Label(header_frame, text="📝 TEXT CIPHER",
                          font=('Segoe UI', 26, 'bold'),
                          fg='#64b5f6', bg='#1a1a2e')
    title_label.grid(row=0, column=0)
    
    subtitle_label = tk.Label(header_frame, text="Secure Text Encryption & Decryption using Hill Cipher",
                             font=('Segoe UI', 11),
                             fg='#90a4ae', bg='#1a1a2e')
    subtitle_label.grid(row=1, column=0, pady=(5, 0))
    
    # ROW 1: Key management section
    key_frame = tk.Frame(window, bg='#16213e', relief='flat')
    key_frame.grid(row=1, column=0, sticky='ew', padx=40, pady=(0, 20))
    key_frame.grid_columnconfigure(0, weight=1)
    
    tk.Label(key_frame, text="🔑 Encryption Key Matrix:",
             font=('Segoe UI', 12, 'bold'),
             fg='white', bg='#16213e').grid(row=0, column=0, pady=(15, 5))
    
    key_entry = scrolledtext.ScrolledText(key_frame, height=3, width=50,
                                         font=('Consolas', 10),
                                         bg='#263238', fg='white',
                                         insertbackground='white',
                                         relief='flat', bd=5,
                                         wrap='none')
    key_entry.grid(row=1, column=0, pady=5)
    key_entry.insert('1.0', "3,3,3;2,5,1;1,2,3")
    
    # Key buttons
    key_btn_frame = tk.Frame(key_frame, bg='#16213e')
    key_btn_frame.grid(row=2, column=0, pady=10)
    
    tk.Label(key_frame, text="💡 Format: Separate matrix rows with ';' and values with ','",
             font=('Segoe UI', 9),
             fg='#78909c', bg='#16213e').grid(row=3, column=0, pady=(5, 15))
    
    # ROW 2: Main content area (expandable)
    content_frame = tk.Frame(window, bg='#1a1a2e')
    content_frame.grid(row=2, column=0, sticky='nsew', padx=40, pady=(0, 20))
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)
    content_frame.grid_columnconfigure(1, weight=1)
    
    # Left panel
    left_frame = tk.Frame(content_frame, bg='#1a1a2e')
    left_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
    left_frame.grid_rowconfigure(1, weight=1)
    left_frame.grid_rowconfigure(3, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)
    
    # Input section
    tk.Label(left_frame, text="📝 Input Text",
             font=('Segoe UI', 12, 'bold'),
             fg='white', bg='#1a1a2e').grid(row=0, column=0, sticky='w', pady=(0, 5))
    
    input_frame = tk.Frame(left_frame, bg='#16213e', relief='flat')
    input_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 15))
    input_frame.grid_rowconfigure(0, weight=1)
    input_frame.grid_columnconfigure(0, weight=1)
    
    msg_box = scrolledtext.ScrolledText(input_frame, width=50, height=8,
                                       font=('Consolas', 10),
                                       bg='#263238', fg='white',
                                       insertbackground='white',
                                       relief='flat', bd=5,
                                       wrap='word',
                                       selectbackground='#37474f',
                                       selectforeground='white')
    msg_box.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    
    # Ciphertext section
    tk.Label(left_frame, text="🔐 Ciphertext",
             font=('Segoe UI', 12, 'bold'),
             fg='white', bg='#1a1a2e').grid(row=2, column=0, sticky='w', pady=(0, 5))
    
    cipher_frame = tk.Frame(left_frame, bg='#16213e', relief='flat')
    cipher_frame.grid(row=3, column=0, sticky='nsew')
    cipher_frame.grid_rowconfigure(0, weight=1)
    cipher_frame.grid_columnconfigure(0, weight=1)
    
    cipher_box = scrolledtext.ScrolledText(cipher_frame, width=50, height=8,
                                          font=('Consolas', 10),
                                          bg='#263238', fg='white',
                                          insertbackground='white',
                                          relief='flat', bd=5,
                                          wrap='word',
                                          selectbackground='#37474f',
                                          selectforeground='white')
    cipher_box.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    
    # Right panel - Output
    right_frame = tk.Frame(content_frame, bg='#1a1a2e')
    right_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
    right_frame.grid_rowconfigure(1, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)
    
    tk.Label(right_frame, text="🔓 Output",
             font=('Segoe UI', 12, 'bold'),
             fg='white', bg='#1a1a2e').grid(row=0, column=0, sticky='w', pady=(0, 5))
    
    output_frame = tk.Frame(right_frame, bg='#16213e', relief='flat')
    output_frame.grid(row=1, column=0, sticky='nsew')
    output_frame.grid_rowconfigure(0, weight=1)
    output_frame.grid_columnconfigure(0, weight=1)
    
    out_box = scrolledtext.ScrolledText(output_frame, width=50, height=20,
                                       font=('Consolas', 10),
                                       bg='#263238', fg='white',
                                       insertbackground='white',
                                       relief='flat', bd=5,
                                       wrap='word',
                                       selectbackground='#37474f',
                                       selectforeground='white')
    out_box.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    # Functions
    def generate_random_key():
        try:
            K = generate_key(3)
            key_str = ";".join(",".join(str(x) for x in row) for row in K)
            key_entry.delete("1.0", "end")
            key_entry.insert("1.0", key_str)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate key:\n{str(e)}")

    def copy_key():
        try:
            key_str = key_entry.get("1.0", "end-1c").strip()
            if not key_str:
                messagebox.showwarning("No Key", "No key to copy.")
                return
            window.clipboard_clear()
            window.clipboard_append(key_str)
            messagebox.showinfo("Copied", "Key copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy key:\n{str(e)}")

    def paste_key():
        try:
            clipboard_content = window.clipboard_get()
            key_entry.delete("1.0", "end")
            key_entry.insert("1.0", clipboard_content)
            messagebox.showinfo("Pasted", "Key pasted from clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste key:\n{str(e)}")

    def encrypt_message():
        msg = msg_box.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showerror("Error", "Enter a message to encrypt")
            return
        
        try:
            key_str = key_entry.get("1.0", "end-1c").strip()
            rows = [[int(x.strip()) for x in r.split(",")] for r in key_str.split(";")]
            K = np.array(rows, dtype=int)
            
            if K.shape[0] != K.shape[1]:
                raise ValueError("Key matrix must be square")
            
            _ = matrix_mod_inv(K, modulus)
            
            cipher = encrypt(msg, K)
            key_str_display = ";".join(",".join(str(x) for x in row) for row in K)

            out_box.delete("1.0", tk.END)
            out_box.insert(tk.END, f"Encryption successful!\n\nCiphertext:\n{cipher}\n\nKey used:\n{key_str_display}")

            cipher_box.delete("1.0", tk.END)
            cipher_box.insert(tk.END, cipher)
            
        except Exception as e:
            messagebox.showerror("Error", f"Encryption failed:\n{str(e)}")

    def decrypt_message():
        cipher = cipher_box.get("1.0", tk.END).strip()
        key_str = key_entry.get("1.0", "end-1c").strip()

        if not cipher or not key_str:
            messagebox.showerror("Error", "Enter ciphertext and key")
            return

        try:
            rows = [[int(x.strip()) for x in r.split(",")] for r in key_str.split(";")]
            K = np.array(rows, dtype=int)
            Kinv = matrix_mod_inv(K, modulus)
            
            plain = decrypt(cipher, Kinv)
            out_box.delete("1.0", tk.END)
            out_box.insert(tk.END, f"Decryption successful!\n\nPlaintext:\n{plain}")
        except Exception as e:
            messagebox.showerror("Error", f"Decryption failed:\n{str(e)}")

    def clear_all():
        msg_box.delete("1.0", tk.END)
        cipher_box.delete("1.0", tk.END)
        out_box.delete("1.0", tk.END)

    # Key buttons
    create_styled_button(key_btn_frame, "🎲 Generate Random Key", generate_random_key, '#2196f3', 18).grid(row=0, column=0, padx=5)
    create_styled_button(key_btn_frame, "📋 Copy Key", copy_key, '#2196f3', 12).grid(row=0, column=1, padx=5)
    create_styled_button(key_btn_frame, "📌 Paste Key", paste_key, '#2196f3', 12).grid(row=0, column=2, padx=5)

    # ROW 3: Action buttons
    btn_frame = tk.Frame(window, bg='#1a1a2e')
    btn_frame.grid(row=3, column=0, pady=20)
    
    create_styled_button(btn_frame, "🔐 Encrypt Message", encrypt_message, '#4caf50').grid(row=0, column=0, padx=10)
    create_styled_button(btn_frame, "🔓 Decrypt Message", decrypt_message, '#ff9800').grid(row=0, column=1, padx=10)
    create_styled_button(btn_frame, "🗑️ Clear All", clear_all, '#9e9e9e').grid(row=0, column=2, padx=10)
    create_styled_button(btn_frame, "🚪 Exit", window.destroy, '#f44336').grid(row=0, column=3, padx=10)

    # ROW 4: Status bar
    status_frame = tk.Frame(window, bg='#263238', height=35)
    status_frame.grid(row=4, column=0, sticky='ew')
    status_frame.grid_propagate(False)
    status_frame.grid_columnconfigure(0, weight=1)
    
    status_label = tk.Label(status_frame, text="Ready - Enter text and key to begin encryption",
                           font=('Segoe UI', 10),
                           fg='#4caf50', bg='#263238')
    status_label.grid(row=0, column=0, sticky='w', padx=15, pady=8)

    if not parent:
        window.mainloop()


if __name__ == "__main__":
    run()