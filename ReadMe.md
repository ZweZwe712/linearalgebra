# Hill Cipher Project (Text, Image, Audio)

This project demonstrates **Hill Cipher encryption and decryption** using **linear algebra** in Python.  
It supports three different modes:
1. **Text-based encryption/decryption**
2. **Image-based encryption/decryption**
3. **Audio-based encryption/decryption (Normal WAV + Morse code)**

---

## 🔹 Features
- Implements **Hill Cipher** using matrix operations (`numpy`).
- **Text mode**: Encrypt/decrypt strings using a given key matrix.
- **Image mode**: Encrypt/decrypt grayscale images (pixel-based Hill cipher).
- **Audio mode**: 
  - Encrypt/decrypt `.wav` audio files (sample-based Hill cipher).
  - Encrypt Morse code derived from text messages.

---

## 🔹 Project Structure

hill-cipher-project/
│── hill/
│ ├── text_cipher.py # Hill Cipher for text
│ ├── image_cipher.py # Hill Cipher for images
│ └── audio_cipher.py # Hill Cipher for audio (normal + morse)
│── utils/
│ ├── matrix_utils.py # modular inverse, matrix ops
│ └── morse_utils.py # morse encode/decode helpers
│── main.py # Entry point (menu)
│── requirements.txt
│── README.md


## 🔹 Installation

Clone the repository and install dependencies:


git clone https://github.com/<your-team>/hill-cipher-project.git
cd hill-cipher-project
pip install -r requirements.txt
🔹 Usage
Run the project:

bash
Copy
Edit
python main.py
Select mode:

mathematica
Copy
Edit
========================================
   Hill Cipher Project - Multi Mode
========================================
Choose an option:
1. Text Mode
2. Image Mode
3. Audio Mode
0. Exit
🔸 Text Mode
Enter a string.

Program will encrypt and decrypt using a 2x2 key matrix.

Example:

pgsql
Copy
Edit
Enter a message: HELLO
Encrypted: MFNCZ
Decrypted: HELLOX
🔸 Image Mode
Provide an image filename (e.g., example.png).

Produces:

example-encoded.png

example-decoded.png

🔸 Audio Mode
Option 1 (Normal WAV):

Provide a .wav file.

Produces encrypted.wav and decrypted.wav.

Option 2 (Morse Code):

Enter text message.

Displays Morse code and encrypts/decrypts it with Hill cipher.

🔹 Team Workflow (GitHub)
Create a GitHub repo, add collaborators.

Each member creates a feature branch:

text-mode

image-mode

audio-mode

Push changes and open Pull Requests.

Merge into main branch after review.

🔹 Future Improvements
Extend to color images (RGB channels).

Add support for audio playback after decryption.

Improve Morse code audio synthesis (generate .wav beeps).

Add a GUI (Tkinter or PyQt).

🔹 References
Original Hill Image Cipher: ilyeshammadi/hill-image-cipher

Linear Algebra concepts from course materials


_____________________________________________________________________
---------------------------------------------------------------------
##FOR MEMBERS##
Each member should:

# Clone repo
git clone https://github.com/your-username/hill-cipher-project.git
cd hill-cipher-project

# Create their own branch for features
git checkout -b text-mode
# (make changes)
git add .
git commit -m "Added text cipher module"
git push origin text-mode


Then open a Pull Request on GitHub → review → merge into main.

⚡ Tip: Always pull latest changes before working:

git pull origin main
