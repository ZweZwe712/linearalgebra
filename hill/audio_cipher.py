import os
import threading
import numpy as np
from scipy.io import wavfile
from utils.matrix_utils import matrix_mod_inv
from utils.morse_utils import text_to_morse, morse_to_text

# GUI/plot imports (optional at runtime; only used when launching GUI)
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False

try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    HAS_WINSOUND = False

def encrypt_audio(path, key_matrix, seed=1234):
    rate, data = wavfile.read(path)
    flat = data.flatten().astype(np.int64)
    n = key_matrix.shape[0]

    # Pad to multiple of n
    while len(flat) % n != 0:
        flat = np.append(flat, 0)

    blocks = flat.reshape(-1, n)

    # --- Hill Cipher Encryption ---
    encrypted = (blocks @ key_matrix.astype(np.int64)) % 65536

    # --- Block Permutation (key-dependent) ---
    np.random.seed(seed)
    perm = np.random.permutation(encrypted.shape[0])
    encrypted = encrypted[perm]

    # --- XOR Masking (key-dependent) ---
    np.random.seed(seed + 1)  # different stream
    mask = np.random.randint(0, 65536, size=encrypted.shape, dtype=np.int64)
    encrypted = (encrypted + mask) % 65536

    # Flatten and truncate back to original length
    encrypted = encrypted.flatten()[:len(data)].astype(np.int16)

    # Save encrypted file
    project_root = os.path.dirname(os.path.dirname(__file__))
    audios_dir = os.path.join(project_root, "audios")
    os.makedirs(audios_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(audios_dir, f"{base}-encrypted.wav")

    wavfile.write(out_path, rate, encrypted)
    print(f"Saved {out_path}")
    return out_path

def decrypt_audio(path, key_matrix, seed=1234):
    rate, data = wavfile.read(path)
    flat = data.flatten().astype(np.int64)
    n = key_matrix.shape[0]

    # Pad to multiple of n
    while len(flat) % n != 0:
        flat = np.append(flat, 0)

    blocks = flat.reshape(-1, n)

    # --- Undo XOR Masking ---
    np.random.seed(seed + 1)  # same as encryption
    mask = np.random.randint(0, 65536, size=blocks.shape, dtype=np.int64)
    blocks = (blocks - mask) % 65536

    # --- Undo Block Permutation ---
    np.random.seed(seed)
    perm = np.random.permutation(blocks.shape[0])
    inv_perm = np.argsort(perm)  # inverse permutation
    blocks = blocks[inv_perm]

    # --- Hill Cipher Decryption ---
    inv_matrix = matrix_mod_inv(key_matrix, 65536).astype(np.int64)
    decrypted = (blocks @ inv_matrix) % 65536

    # Flatten and truncate back to original length
    decrypted = decrypted.flatten()[:len(data)].astype(np.int16)

    # Save decrypted file
    project_root = os.path.dirname(os.path.dirname(__file__))
    audios_dir = os.path.join(project_root, "audios")
    os.makedirs(audios_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(audios_dir, f"{base}-decrypted.wav")

    wavfile.write(out_path, rate, decrypted)
    print(f"Saved {out_path}")
    return out_path

def run():
    """Launch the Audio GUI with simultaneous waveforms."""
    if not GUI_AVAILABLE:
        print("GUI dependencies not available. Please ensure tkinter and matplotlib are installed.")
        return

    key_matrix = np.array([[3, 3], [2, 5]], dtype=int)

    class AudioCipherGUI:
        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.root.title("Audio Cipher - GUI")

            self.current_path = None
            self.encrypted_path = "encrypted.wav"
            self.decrypted_path = "decrypted.wav"
            self.key_matrix = key_matrix

            self._build_controls()
            self._build_plots()

        def _build_controls(self) -> None:
            btn_frame = tk.Frame(self.root)
            btn_frame.pack(fill=tk.X, padx=8, pady=8)

            tk.Button(btn_frame, text="Import Audio", command=self.on_import).pack(side=tk.LEFT, padx=4)
            tk.Button(btn_frame, text="Play Original", command=self.on_play_original).pack(side=tk.LEFT, padx=4)

            tk.Button(btn_frame, text="Encrypt Audio", command=self.on_encrypt).pack(side=tk.LEFT, padx=12)
            tk.Button(btn_frame, text="Play Encrypted", command=self.on_play_encrypted).pack(side=tk.LEFT, padx=4)

            tk.Button(btn_frame, text="Decrypt Audio", command=self.on_decrypt).pack(side=tk.LEFT, padx=12)
            tk.Button(btn_frame, text="Play Decrypted", command=self.on_play_decrypted).pack(side=tk.LEFT, padx=4)

            tk.Button(btn_frame, text="        Exit        ", command=self.back_to_main).pack(side=tk.LEFT, padx=12)

        def _build_plots(self) -> None:
            fig = Figure(figsize=(11, 7.5), dpi=100)
            self.ax_orig = fig.add_subplot(311)
            self.ax_enc = fig.add_subplot(312)
            self.ax_dec = fig.add_subplot(313)

            for ax, title in [
                (self.ax_orig, "Original"),
                (self.ax_enc, "Encrypted"),
                (self.ax_dec, "Decrypted"),
            ]:
                ax.set_title(title)
                ax.set_xlabel("Samples")
                ax.set_ylabel("Amplitude")
                ax.grid(True, linewidth=0.3)

            self.canvas = FigureCanvasTkAgg(fig, master=self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        def _load_wav_for_plot(self, path: str):
            try:
                rate, data = wavfile.read(path)
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to read WAV: {exc}")
                return None

            if data.ndim == 2:
                data = data.mean(axis=1)

            max_points = 200_000
            if data.shape[0] > max_points:
                step = int(np.ceil(data.shape[0] / max_points))
                data = data[::step]
            return data

        def _refresh_plots(self) -> None:
            # Clear and redraw all three waveforms if available
            for ax in [self.ax_orig, self.ax_enc, self.ax_dec]:
                ax.clear()
                ax.grid(True, linewidth=0.3)
                ax.set_xlabel("Samples")
                ax.set_ylabel("Amplitude")

            if self.current_path and os.path.exists(self.current_path):
                d = self._load_wav_for_plot(self.current_path)
                if d is not None:
                    self.ax_orig.set_title("Original")
                    self.ax_orig.plot(d, color="#1f77b4", linewidth=0.7)
            else:
                self.ax_orig.set_title("Original (no file)")

            if os.path.exists(self.encrypted_path):
                d = self._load_wav_for_plot(self.encrypted_path)
                if d is not None:
                    self.ax_enc.set_title("Encrypted")
                    self.ax_enc.plot(d, color="#ff7f0e", linewidth=0.7)
            else:
                self.ax_enc.set_title("Encrypted (none)")

            if os.path.exists(self.decrypted_path):
                d = self._load_wav_for_plot(self.decrypted_path)
                if d is not None:
                    self.ax_dec.set_title("Decrypted")
                    self.ax_dec.plot(d, color="#2ca02c", linewidth=0.7)
            else:
                self.ax_dec.set_title("Decrypted (none)")

            self.canvas.figure.tight_layout()
            self.canvas.draw_idle()

        def _play_wav(self, path: str) -> None:
            if not HAS_WINSOUND:
                messagebox.showinfo("Playback", "winsound not available on this platform.")
                return
            if not os.path.exists(path):
                messagebox.showerror("Error", f"File not found: {path}")
                return

            def _play():
                try:
                    winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                except Exception as exc:
                    messagebox.showerror("Error", f"Failed to play audio: {exc}")

            threading.Thread(target=_play, daemon=True).start()

        def on_import(self) -> None:
            path = filedialog.askopenfilename(
                title="Select WAV file",
                filetypes=[("WAV files", "*.wav"), ("All files", "*.*")],
                initialdir=os.getcwd(),
            )
            if not path:
                return
            try:
                wavfile.read(path)  # Validate
            except Exception as exc:
                messagebox.showerror("Error", f"Failed to read WAV: {exc}")
                return
            self.current_path = path
            self._refresh_plots()

        def on_play_original(self) -> None:
            if not self.current_path:
                messagebox.showinfo("Info", "Please import a WAV file first.")
                return
            self._play_wav(self.current_path)

        def on_encrypt(self) -> None:
            if not self.current_path:
                messagebox.showinfo("Info", "Please import a WAV file first.")
                return
            try:
                out = encrypt_audio(self.current_path, self.key_matrix)
            except Exception as exc:
                messagebox.showerror("Error", f"Encryption failed: {exc}")
                return
            if out:
                self.encrypted_path = out
            self._refresh_plots()
            messagebox.showinfo("Saved", f"Encrypted file saved to {self.encrypted_path}")

        def on_play_encrypted(self) -> None:
            if not os.path.exists(self.encrypted_path):
                messagebox.showinfo("Info", "Encrypt an audio file first.")
                return
            self._play_wav(self.encrypted_path)

        def on_decrypt(self) -> None:
            source = self.encrypted_path if os.path.exists(self.encrypted_path) else self.current_path
            if not source:
                messagebox.showinfo("Info", "Please import or encrypt a WAV file first.")
                return
            try:
                out = decrypt_audio(source, self.key_matrix)
            except Exception as exc:
                messagebox.showerror("Error", f"Decryption failed: {exc}")
                return
            if out:
                self.decrypted_path = out
            self._refresh_plots()
            messagebox.showinfo("Saved", f"Decrypted file saved to {self.decrypted_path}")

        def on_play_decrypted(self) -> None:
            if not os.path.exists(self.decrypted_path):
                messagebox.showinfo("Info", "Decrypt an audio file first.")
                return
            self._play_wav(self.decrypted_path)

        def back_to_main(self) -> None:
            """Close the current window and return to main menu."""
            self.root.destroy()

    root = tk.Tk()
    app = AudioCipherGUI(root)
    root.geometry("1200x800")
    app._refresh_plots()
    root.mainloop()
