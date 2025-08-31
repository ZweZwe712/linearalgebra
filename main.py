import tkinter as tk
from hill import text_cipher, image_cipher, audio_cipher

def open_text():
    try:
        text_cipher.run(parent=root)
    except TypeError:
        text_cipher.run()

def open_image_encoder():
    try:
        image_cipher.run_encoder(parent=root)
    except TypeError:
        image_cipher.run_encoder()

def open_image_decoder():
    try:
        image_cipher.run_decoder(parent=root)
    except TypeError:
        image_cipher.run_decoder()

def open_audio():
    try:
        audio_cipher.run(parent=root)
    except TypeError:
        audio_cipher.run()

root = tk.Tk()
root.title("Hill Cipher Project - Launcher")
root.geometry("1200x800")

tk.Label(root, text="--**Hill Cipher**--", font=("Arial", 32, "bold")).pack(pady=32)
tk.Button(root, text="Open Text Cipher GUI", width=28, command=open_text).pack(pady=6)
tk.Button(root, text="Open Image Encoder", width=28, command=open_image_encoder).pack(pady=6)
tk.Button(root, text="Open Image Decoder", width=28, command=open_image_decoder).pack(pady=6)
tk.Button(root, text="Open Audio Cipher GUI", width=28, command=open_audio).pack(pady=6)
tk.Button(root, text="Exit", width=28, command=root.destroy).pack(pady=16)

root.mainloop()

