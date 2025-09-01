import os
import threading
import numpy as np
from scipy.io import wavfile
from utils.matrix_utils import matrix_mod_inv
from utils.morse_utils import text_to_morse, morse_to_text

# GUI/plot imports (optional at runtime; only used when launching GUI)
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
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


class ModernAudioCipher:
    def __init__(self, parent=None):
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.current_path = None
        self.encrypted_path = "encrypted.wav"
        self.decrypted_path = "decrypted.wav"
        self.key_matrix = np.array([[3, 3], [2, 5]], dtype=int)
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Configure the main window"""
        self.window.title("🎵 Audio Cipher - Hill Encryption Suite")
        self.window.geometry("1300x900")
        self.window.configure(bg='#1a1a2e')
        self.window.minsize(1200, 800)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1300 // 2)
        y = (self.window.winfo_screenheight() // 2) - (900 // 2)
        self.window.geometry(f"1300x900+{x}+{y}")
        
        # Configure grid
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        main_frame = tk.Frame(self.window, bg='#1a1a2e')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Waveform display area
        self.create_waveform_display(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create header section"""
        header_frame = tk.Frame(parent, bg='#1a1a2e')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 25))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = tk.Label(header_frame, text="🎵 AUDIO CIPHER",
                        font=('Segoe UI', 26, 'bold'),
                        fg='#64b5f6', bg='#1a1a2e')
        title.grid(row=0, column=0)
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="Secure Audio Encryption & Decryption with Waveform Visualization",
                           font=('Segoe UI', 11),
                           fg='#90a4ae', bg='#1a1a2e')
        subtitle.grid(row=1, column=0, pady=(5, 0))
        
        # Decorative line
        line_frame = tk.Frame(header_frame, height=2, bg='#64b5f6')
        line_frame.grid(row=2, column=0, sticky='ew', pady=15, padx=350)
    
    def create_control_panel(self, parent):
        """Create control panel with buttons and info"""
        control_frame = tk.Frame(parent, bg='#16213e', relief='flat')
        control_frame.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        control_frame.grid_columnconfigure(0, weight=1)
        
        # File operations section
        file_section = tk.Frame(control_frame, bg='#16213e')
        file_section.grid(row=0, column=0, sticky='ew', padx=20, pady=15)
        file_section.grid_columnconfigure(1, weight=1)
        file_section.grid_columnconfigure(3, weight=1)
        file_section.grid_columnconfigure(5, weight=1)
        
        # Import and play original
        self.create_control_button(file_section, "📂 Import Audio", self.import_audio, '#2196f3').grid(row=0, column=0, padx=5)
        self.create_control_button(file_section, "▶️ Play Original", self.play_original, '#4caf50').grid(row=0, column=1, padx=5)
        
        # Encryption controls
        self.create_control_button(file_section, "🔐 Encrypt", self.encrypt_audio_file, '#ff9800').grid(row=0, column=2, padx=5)
        self.create_control_button(file_section, "▶️ Play Encrypted", self.play_encrypted, '#ff5722').grid(row=0, column=3, padx=5)
        
        # Decryption controls
        self.create_control_button(file_section, "🔓 Decrypt", self.decrypt_audio_file, '#9c27b0').grid(row=0, column=4, padx=5)
        self.create_control_button(file_section, "▶️ Play Decrypted", self.play_decrypted, '#00bcd4').grid(row=0, column=5, padx=5)
        
        # Exit button
        self.create_control_button(file_section, "🚪 Exit", self.window.destroy, '#f44336').grid(row=0, column=6, padx=5)
        
        # Info section
        info_section = tk.Frame(control_frame, bg='#16213e')
        info_section.grid(row=1, column=0, sticky='ew', padx=20, pady=(0, 15))
        info_section.grid_columnconfigure(0, weight=1)
        
        # Current file info
        self.file_info_label = tk.Label(info_section, text="📁 No audio file loaded",
                                       font=('Segoe UI', 10, 'bold'),
                                       fg='#78909c', bg='#16213e')
        self.file_info_label.grid(row=0, column=0, sticky='w')
        
        # Key matrix info
        key_info = tk.Label(info_section, text=f"🔑 Encryption Key: {self.key_matrix.tolist()}",
                           font=('Segoe UI', 9),
                           fg='#90a4ae', bg='#16213e')
        key_info.grid(row=1, column=0, sticky='w', pady=(5, 0))
    
    def create_control_button(self, parent, text, command, color):
        """Create a styled control button"""
        btn = tk.Button(parent, text=text,
                       font=('Segoe UI', 10, 'bold'),
                       bg=color, fg='white',
                       activebackground=self.darken_color(color),
                       activeforeground='white',
                       relief='flat', bd=0,
                       cursor='hand2',
                       command=command,
                       width=15, height=2)
        
        # Hover effects
        def on_enter(e):
            btn.configure(bg=self.darken_color(color))
        
        def on_leave(e):
            btn.configure(bg=color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def darken_color(self, color):
        """Darken a hex color"""
        color_map = {
            '#2196f3': '#1976d2',
            '#4caf50': '#388e3c',
            '#ff9800': '#f57c00',
            '#ff5722': '#e64a19',
            '#9c27b0': '#7b1fa2',
            '#00bcd4': '#0097a7',
            '#f44336': '#d32f2f'
        }
        return color_map.get(color, color)
    
    def create_waveform_display(self, parent):
        """Create waveform visualization area"""
        # Create matplotlib figure
        self.fig = Figure(figsize=(13, 8), dpi=100, facecolor='#1a1a2e')
        self.ax_orig = self.fig.add_subplot(311, facecolor='#263238')
        self.ax_enc = self.fig.add_subplot(312, facecolor='#263238')
        self.ax_dec = self.fig.add_subplot(313, facecolor='#263238')
        
        # Configure axes
        axes_config = [
            (self.ax_orig, "🎧 Original Audio Waveform", '#4caf50'),
            (self.ax_enc, "🔐 Encrypted Audio Waveform", '#ff9800'),
            (self.ax_dec, "🔓 Decrypted Audio Waveform", '#2196f3'),
        ]
        
        for ax, title, color in axes_config:
            ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=15)
            ax.set_xlabel("Time (samples)", color='white', fontsize=10)
            ax.set_ylabel("Amplitude", color='white', fontsize=10)
            ax.grid(True, alpha=0.3, color='#37474f')
            ax.tick_params(colors='white', labelsize=8)
            
            # Style spines
            for spine in ax.spines.values():
                spine.set_color('#37474f')
                spine.set_linewidth(1)
        
        self.fig.tight_layout(pad=2.0)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky='nsew', pady=(0, 15))
    
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_frame = tk.Frame(parent, bg='#263238', height=35)
        self.status_frame.grid(row=3, column=0, sticky='ew')
        self.status_frame.grid_propagate(False)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = tk.Label(self.status_frame, 
                                    text="🔊 Ready - Import an audio file to begin encryption",
                                    font=('Segoe UI', 10),
                                    fg='#4caf50', bg='#263238')
        self.status_label.grid(row=0, column=0, padx=15, pady=8, sticky='w')
    
    def update_status(self, message, color='#4caf50'):
        """Update status bar message"""
        self.status_label.configure(text=message, fg=color)
        self.window.update_idletasks()
    
    def load_wav_for_plot(self, path):
        """Load WAV file data for plotting"""
        try:
            rate, data = wavfile.read(path)
            if data.ndim == 2:
                data = data.mean(axis=1)
            
            # Downsample for display if too large
            max_points = 50000
            if len(data) > max_points:
                step = len(data) // max_points
                data = data[::step]
            
            return data, rate
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audio file:\n{str(e)}")
            return None, None
    
    def refresh_waveforms(self):
        """Refresh all waveform plots"""
        # Clear all axes
        for ax in [self.ax_orig, self.ax_enc, self.ax_dec]:
            ax.clear()
        
        # Reconfigure axes after clearing
        axes_config = [
            (self.ax_orig, "🎧 Original Audio Waveform", '#4caf50'),
            (self.ax_enc, "🔐 Encrypted Audio Waveform", '#ff9800'),
            (self.ax_dec, "🔓 Decrypted Audio Waveform", '#2196f3'),
        ]
        
        for ax, title, color in axes_config:
            ax.set_facecolor('#263238')
            ax.set_title(title, color='white', fontsize=12, fontweight='bold', pad=15)
            ax.set_xlabel("Time (samples)", color='white', fontsize=10)
            ax.set_ylabel("Amplitude", color='white', fontsize=10)
            ax.grid(True, alpha=0.3, color='#37474f')
            ax.tick_params(colors='white', labelsize=8)
            
            # Style spines
            for spine in ax.spines.values():
                spine.set_color('#37474f')
                spine.set_linewidth(1)
        
        # Plot original audio if available
        if self.current_path and os.path.exists(self.current_path):
            data, rate = self.load_wav_for_plot(self.current_path)
            if data is not None:
                self.ax_orig.plot(data, color='#4caf50', linewidth=0.8, alpha=0.8)
                self.ax_orig.set_title("🎧 Original Audio Waveform", color='white', fontsize=12, fontweight='bold', pad=15)
            else:
                self.ax_orig.text(0.5, 0.5, "❌ Failed to load original audio", 
                                 transform=self.ax_orig.transAxes, ha='center', va='center',
                                 color='#f44336', fontsize=12)
        else:
            self.ax_orig.text(0.5, 0.5, "📁 No original audio loaded", 
                             transform=self.ax_orig.transAxes, ha='center', va='center',
                             color='#78909c', fontsize=12)
        
        # Plot encrypted audio if available
        if os.path.exists(self.encrypted_path):
            data, rate = self.load_wav_for_plot(self.encrypted_path)
            if data is not None:
                self.ax_enc.plot(data, color='#ff9800', linewidth=0.8, alpha=0.8)
                self.ax_enc.set_title("🔐 Encrypted Audio Waveform", color='white', fontsize=12, fontweight='bold', pad=15)
            else:
                self.ax_enc.text(0.5, 0.5, "❌ Failed to load encrypted audio", 
                                transform=self.ax_enc.transAxes, ha='center', va='center',
                                color='#f44336', fontsize=12)
        else:
            self.ax_enc.text(0.5, 0.5, "🔐 No encrypted audio available", 
                            transform=self.ax_enc.transAxes, ha='center', va='center',
                            color='#78909c', fontsize=12)
        
        # Plot decrypted audio if available
        if os.path.exists(self.decrypted_path):
            data, rate = self.load_wav_for_plot(self.decrypted_path)
            if data is not None:
                self.ax_dec.plot(data, color='#2196f3', linewidth=0.8, alpha=0.8)
                self.ax_dec.set_title("🔓 Decrypted Audio Waveform", color='white', fontsize=12, fontweight='bold', pad=15)
            else:
                self.ax_dec.text(0.5, 0.5, "❌ Failed to load decrypted audio", 
                                transform=self.ax_dec.transAxes, ha='center', va='center',
                                color='#f44336', fontsize=12)
        else:
            self.ax_dec.text(0.5, 0.5, "🔓 No decrypted audio available", 
                            transform=self.ax_dec.transAxes, ha='center', va='center',
                            color='#78909c', fontsize=12)
        
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw_idle()
    
    def play_audio_file(self, path, file_type="audio"):
        """Play audio file using winsound"""
        if not HAS_WINSOUND:
            messagebox.showinfo("Playback Not Available", 
                               "Audio playback is not available on this platform.\n" +
                               "winsound module is required for playback functionality.")
            return
            
        if not os.path.exists(path):
            messagebox.showerror("File Not Found", f"{file_type.title()} file not found:\n{path}")
            return
        
        def play_audio():
            try:
                self.update_status(f"🔊 Playing {file_type} audio...", '#2196f3')
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                # Reset status after a delay
                self.window.after(2000, lambda: self.update_status("🔊 Audio playback started"))
            except Exception as e:
                messagebox.showerror("Playback Error", f"Failed to play {file_type} audio:\n{str(e)}")
                self.update_status("❌ Playback failed", '#f44336')
        
        # Run playback in separate thread to prevent GUI blocking
        threading.Thread(target=play_audio, daemon=True).start()
    
    def import_audio(self):
        """Import audio file"""
        path = filedialog.askopenfilename(
            parent=self.window,
            title="Select Audio File",
            filetypes=[
                ("WAV files", "*.wav"),
                ("Audio files", "*.wav *.mp3 *.flac"),
                ("All files", "*.*")
            ],
            initialdir=os.getcwd()
        )
        
        if not path:
            return
        
        try:
            self.update_status("📂 Loading audio file...", '#2196f3')
            
            # Validate audio file
            rate, data = wavfile.read(path)
            
            # Update current path and file info
            self.current_path = path
            filename = os.path.basename(path)
            duration = len(data) / rate if rate > 0 else 0
            file_size = os.path.getsize(path) / 1024  # KB
            
            # Update file info display
            info_text = f"📁 {filename} | {duration:.1f}s | {rate}Hz | {file_size:.1f}KB"
            self.file_info_label.configure(text=info_text, fg='#4caf50')
            
            # Refresh waveform display
            self.refresh_waveforms()
            
            self.update_status(f"✅ Audio file loaded: {filename}")
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import audio file:\n{str(e)}")
            self.update_status("❌ Failed to load audio file", '#f44336')
    
    def play_original(self):
        """Play original audio file"""
        if not self.current_path:
            messagebox.showinfo("No File", "Please import an audio file first.")
            return
        self.play_audio_file(self.current_path, "original")
    
    def encrypt_audio_file(self):
        """Encrypt the current audio file"""
        if not self.current_path:
            messagebox.showinfo("No File", "Please import an audio file first.")
            return
        
        try:
            self.update_status("🔐 Encrypting audio file...", '#ff9800')
            
            # Perform encryption
            encrypted_path = encrypt_audio(self.current_path, self.key_matrix)
            
            if encrypted_path:
                self.encrypted_path = encrypted_path
                self.refresh_waveforms()
                
                filename = os.path.basename(encrypted_path)
                self.update_status(f"✅ Audio encrypted successfully: {filename}")
                messagebox.showinfo("Encryption Complete", 
                                   f"Audio file encrypted successfully!\n\nSaved as: {filename}")
            else:
                raise Exception("Encryption returned empty path")
                
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Failed to encrypt audio:\n{str(e)}")
            self.update_status("❌ Encryption failed", '#f44336')
    
    def play_encrypted(self):
        """Play encrypted audio file"""
        if not os.path.exists(self.encrypted_path):
            messagebox.showinfo("No Encrypted File", "Please encrypt an audio file first.")
            return
        self.play_audio_file(self.encrypted_path, "encrypted")
    
    def decrypt_audio_file(self):
        """Decrypt the encrypted audio file"""
        source_path = self.encrypted_path if os.path.exists(self.encrypted_path) else self.current_path
        
        if not source_path:
            messagebox.showinfo("No File", "Please import or encrypt an audio file first.")
            return
        
        try:
            self.update_status("🔓 Decrypting audio file...", '#9c27b0')
            
            # Perform decryption
            decrypted_path = decrypt_audio(source_path, self.key_matrix)
            
            if decrypted_path:
                self.decrypted_path = decrypted_path
                self.refresh_waveforms()
                
                filename = os.path.basename(decrypted_path)
                self.update_status(f"✅ Audio decrypted successfully: {filename}")
                messagebox.showinfo("Decryption Complete", 
                                   f"Audio file decrypted successfully!\n\nSaved as: {filename}")
            else:
                raise Exception("Decryption returned empty path")
                
        except Exception as e:
            messagebox.showerror("Decryption Error", f"Failed to decrypt audio:\n{str(e)}")
            self.update_status("❌ Decryption failed", '#f44336')
    
    def play_decrypted(self):
        """Play decrypted audio file"""
        if not os.path.exists(self.decrypted_path):
            messagebox.showinfo("No Decrypted File", "Please decrypt an audio file first.")
            return
        self.play_audio_file(self.decrypted_path, "decrypted")
    
    def run(self):
        """Start the application"""
        # Initialize the display
        self.refresh_waveforms()
        
        if not self.parent:
            self.window.mainloop()


def run(parent=None):
    """Launch the modern Audio Cipher GUI"""
    if not GUI_AVAILABLE:
        messagebox.showerror("Dependencies Missing", 
                           "GUI dependencies not available.\n" +
                           "Please ensure tkinter and matplotlib are installed.")
        return
    
    app = ModernAudioCipher(parent)
    if not parent:
        app.run()


if __name__ == "__main__":
    run()