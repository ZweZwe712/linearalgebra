import tkinter as tk
from tkinter import ttk, messagebox
from hill import text_cipher, image_cipher, audio_cipher
import time

class HillCipherLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_styles()
        self.create_widgets()
        self.create_animations()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("🔐 Hill Cipher Suite - Advanced Cryptography Toolkit")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.root.configure(bg='#1a1a2e')
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        # Configure grid weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_styles(self):
        """Create custom styles for ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button style
        style.configure('Modern.TButton',
                       background='#16213e',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'),
                       relief='flat')
        
        style.map('Modern.TButton',
                 background=[('active', '#0f3460'),
                           ('pressed', '#0d2a4f')])
        
        # Configure frame style
        style.configure('Modern.TFrame',
                       background='#1a1a2e',
                       borderwidth=0)
    
    def create_widgets(self):
        """Create and arrange all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.grid(row=0, column=0, sticky='nsew', padx=40, pady=30)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header section
        self.create_header(main_frame)
        
        # Description section
        self.create_description(main_frame)
        
        # Button section
        self.create_buttons(main_frame)
        
        # Footer section
        self.create_footer(main_frame)
    
    def create_header(self, parent):
        """Create the header section with title and subtitle"""
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, pady=(0, 30), sticky='ew')
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Main title with gradient effect simulation
        title_label = tk.Label(header_frame, 
                              text="🔐 HILL CIPHER SUITE",
                              font=('Segoe UI', 28, 'bold'),
                              fg='#64b5f6',
                              bg='#1a1a2e')
        title_label.grid(row=0, column=0, pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Advanced Cryptography Toolkit",
                                 font=('Segoe UI', 12),
                                 fg='#90a4ae',
                                 bg='#1a1a2e')
        subtitle_label.grid(row=1, column=0)
        
        # Decorative line
        line_frame = tk.Frame(header_frame, height=2, bg='#64b5f6')
        line_frame.grid(row=2, column=0, sticky='ew', pady=15, padx=200)
    
    def create_description(self, parent):
        """Create description section"""
        desc_frame = ttk.Frame(parent, style='Modern.TFrame')
        desc_frame.grid(row=1, column=0, pady=(0, 40), sticky='ew')
        desc_frame.grid_columnconfigure(0, weight=1)
        
        desc_text = """Select a cryptographic operation to begin securing your data.
Each tool uses advanced Hill Cipher algorithms for maximum security."""
        
        desc_label = tk.Label(desc_frame,
                             text=desc_text,
                             font=('Segoe UI', 11),
                             fg='#b0bec5',
                             bg='#1a1a2e',
                             justify='center',
                             wraplength=600)
        desc_label.grid(row=0, column=0)
    
    def create_buttons(self, parent):
        """Create the main action buttons"""
        button_frame = ttk.Frame(parent, style='Modern.TFrame')
        button_frame.grid(row=2, column=0, pady=(0, 40), sticky='ew')
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Button configurations
        buttons_config = [
            ("📝 TEXT ENCRYPTION", "Encrypt and decrypt text messages", self.open_text, 0, 0),
            ("🖼️ IMAGE ENCODER", "Hide secret data within images", self.open_image_encoder, 0, 1),
            ("🔍 IMAGE DECODER", "Extract hidden data from images", self.open_image_decoder, 1, 0),
            ("🎵 AUDIO ENCRYPTION", "Secure audio files with encryption", self.open_audio, 1, 1),
        ]
        
        self.buttons = []
        for text, desc, command, row, col in buttons_config:
            btn_container = self.create_button_container(button_frame, text, desc, command)
            btn_container.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            button_frame.grid_rowconfigure(row, weight=1)
        
        # Exit button (spans both columns)
        exit_container = self.create_exit_button(button_frame)
        exit_container.grid(row=2, column=0, columnspan=2, pady=(30, 0), sticky='ew')
    
    def create_button_container(self, parent, text, description, command):
        """Create a container for each main button with description"""
        container = tk.Frame(parent, bg='#16213e', relief='flat', bd=1)
        
        # Button
        btn = tk.Button(container,
                       text=text,
                       font=('Segoe UI', 12, 'bold'),
                       bg='#16213e',
                       fg='white',
                       activebackground='#0f3460',
                       activeforeground='white',
                       relief='flat',
                       bd=0,
                       cursor='hand2',
                       command=command,
                       height=3,
                       width=20)
        btn.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Description
        desc_label = tk.Label(container,
                             text=description,
                             font=('Segoe UI', 9),
                             fg='#90a4ae',
                             bg='#16213e',
                             wraplength=180)
        desc_label.pack(pady=(0, 10))
        
        # Hover effects
        def on_enter(e):
            container.configure(bg='#0f3460')
            btn.configure(bg='#0f3460')
            desc_label.configure(bg='#0f3460')
        
        def on_leave(e):
            container.configure(bg='#16213e')
            btn.configure(bg='#16213e')
            desc_label.configure(bg='#16213e')
        
        container.bind("<Enter>", on_enter)
        container.bind("<Leave>", on_leave)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        desc_label.bind("<Enter>", on_enter)
        desc_label.bind("<Leave>", on_leave)
        
        self.buttons.append(container)
        return container
    
    def create_exit_button(self, parent):
        """Create the exit button"""
        exit_container = tk.Frame(parent, bg='#d32f2f', relief='flat', bd=1)
        
        exit_btn = tk.Button(exit_container,
                           text="🚪 EXIT APPLICATION",
                           font=('Segoe UI', 12, 'bold'),
                           bg='#d32f2f',
                           fg='white',
                           activebackground='#b71c1c',
                           activeforeground='white',
                           relief='flat',
                           bd=0,
                           cursor='hand2',
                           command=self.safe_exit,
                           height=2)
        exit_btn.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Hover effect
        def on_enter(e):
            exit_container.configure(bg='#b71c1c')
            exit_btn.configure(bg='#b71c1c')
        
        def on_leave(e):
            exit_container.configure(bg='#d32f2f')
            exit_btn.configure(bg='#d32f2f')
        
        exit_container.bind("<Enter>", on_enter)
        exit_container.bind("<Leave>", on_leave)
        exit_btn.bind("<Enter>", on_enter)
        exit_btn.bind("<Leave>", on_leave)
        
        return exit_container
    
    def create_footer(self, parent):
        """Create footer with status and info"""
        footer_frame = ttk.Frame(parent, style='Modern.TFrame')
        footer_frame.grid(row=3, column=0, sticky='ew')
        footer_frame.grid_columnconfigure(1, weight=1)
        
        # Status indicator
        status_label = tk.Label(footer_frame,
                               text="🟢 System Ready",
                               font=('Segoe UI', 9),
                               fg='#4caf50',
                               bg='#1a1a2e')
        status_label.grid(row=0, column=0, sticky='w')
        
        # Version info
        version_label = tk.Label(footer_frame,
                                text="Hill Cipher Suite v2.0 | Secure • Fast • Reliable",
                                font=('Segoe UI', 9),
                                fg='#607d8b',
                                bg='#1a1a2e')
        version_label.grid(row=0, column=1, sticky='e')
    
    def create_animations(self):
        """Add subtle animations and effects"""
        self.animate_title()
    
    def animate_title(self):
        """Simple title animation"""
        # This could be expanded for more complex animations
        pass
    
    def show_loading(self, message="Loading..."):
        """Show loading indicator"""
        loading_window = tk.Toplevel(self.root)
        loading_window.title("Loading")
        loading_window.geometry("300x100")
        loading_window.configure(bg='#1a1a2e')
        loading_window.transient(self.root)
        loading_window.grab_set()
        
        # Center the loading window
        loading_window.update_idletasks()
        x = (loading_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (loading_window.winfo_screenheight() // 2) - (100 // 2)
        loading_window.geometry(f"300x100+{x}+{y}")
        
        tk.Label(loading_window,
                text=message,
                font=('Segoe UI', 12),
                fg='white',
                bg='#1a1a2e').pack(expand=True)
        
        loading_window.update()
        return loading_window
    
    def open_text(self):
        """Launch text cipher with loading animation"""
        loading = self.show_loading("Opening Text Cipher...")
        self.root.after(500, lambda: self.execute_cipher_function(text_cipher, 'run', loading))
    
    def open_image_encoder(self):
        """Launch image encoder with loading animation"""
        loading = self.show_loading("Opening Image Encoder...")
        self.root.after(500, lambda: self.execute_cipher_function(image_cipher, 'run_encoder', loading))
    
    def open_image_decoder(self):
        """Launch image decoder with loading animation"""
        loading = self.show_loading("Opening Image Decoder...")
        self.root.after(500, lambda: self.execute_cipher_function(image_cipher, 'run_decoder', loading))
    
    def open_audio(self):
        """Launch audio cipher with loading animation"""
        loading = self.show_loading("Opening Audio Cipher...")
        self.root.after(500, lambda: self.execute_cipher_function(audio_cipher, 'run', loading))
    
    def execute_cipher_function(self, cipher_module, method_name, loading_window):
        """Execute cipher function with error handling"""
        try:
            loading_window.destroy()
            method = getattr(cipher_module, method_name)
            try:
                method(parent=self.root)
            except TypeError:
                method()
        except Exception as e:
            loading_window.destroy()
            messagebox.showerror("Error", f"Failed to open cipher module:\n{str(e)}")
    
    def safe_exit(self):
        """Safe exit with confirmation"""
        if messagebox.askyesno("Exit Confirmation", 
                              "Are you sure you want to exit the Hill Cipher Suite?",
                              icon='question'):
            self.root.quit()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Create and run the application
if __name__ == "__main__":
    app = HillCipherLauncher()
    app.run()