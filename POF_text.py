import numpy as np
from hill.text_cipher import encrypt_text

key_matrix = np.array([[3, 3],
                       [2, 5]])

message = "HELLO"
result = encrypt_text(message, key_matrix, verbose=True)
print("\nEncrypted message:", result)
