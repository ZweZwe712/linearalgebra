from hill.image_cipher import Hill
import numpy as np
from PIL import Image

key_matrix = np.array([[3, 3],
                       [2, 5]])

hill = Hill(key_matrix)
img = Image.open("image.png").convert("L")
pixels = np.array(img, dtype=np.uint8)

# Run encryption with verbose output
encrypted = hill.encode(pixels, verbose=True)
