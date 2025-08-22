MORSE_CODE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', ' ': '/'
}

def text_to_morse(text):
    return ' '.join(MORSE_CODE.get(c.upper(), '') for c in text)

def morse_to_text(morse):
    reverse_map = {v: k for k, v in MORSE_CODE.items()}
    return ''.join(reverse_map.get(code, '') for code in morse.split(' '))
