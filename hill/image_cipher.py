import os
import pickle
import numpy as np
import imageio.v2 as imageio
from numpy.linalg import inv, det
from math import gcd
import numpy as np
from math import gcd
import pytest


def mod_matrix_inv(matrix: np.ndarray, modulus: int) -> np.ndarray:
    """Compute modular inverse of a square matrix using integer adjugate method."""
    n = matrix.shape[0]
    det_val = int(round(np.linalg.det(matrix))) % modulus

    if gcd(det_val, modulus) != 1:
        raise ValueError(f"Matrix determinant {det_val} not invertible mod {modulus}")

    # Modular inverse of determinant
    det_inv = pow(det_val, -1, modulus)

    # Compute cofactor matrix
    cofactors = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            minor = np.delete(np.delete(matrix, i, axis=0), j, axis=1)
            cofactors[i, j] = ((-1) ** (i + j)) * int(round(np.linalg.det(minor)))

    # Adjugate is transpose of cofactor matrix
    adjugate = cofactors.T % modulus

    # Final inverse
    matrix_mod_inv = (det_inv * adjugate) % modulus
    return matrix_mod_inv.astype(int)


# ---------------------- PYTESTS ----------------------
@pytest.mark.parametrize("n", [2, 3, 4])
def test_mod_matrix_inv_random(n):
    modulus = 256
    for _ in range(10):
        while True:
            mat = np.random.randint(0, modulus, (n, n))
            det_val = int(round(np.linalg.det(mat))) % modulus
            if det_val != 0 and gcd(det_val, modulus) == 1:
                break
        inv_mat = mod_matrix_inv(mat, modulus)
        identity = (mat @ inv_mat) % modulus
        assert np.array_equal(identity, np.eye(n, dtype=int)), f"Inverse check failed for matrix {mat}"




class Hill:
    def __init__(self, data, file_name, key_path=None, chunk=3):
        self.data = data
        self.chunk = chunk

        if key_path:
            with open(key_path, "rb") as f:
                self._key = pickle.load(f)
        else:
            key_file = file_name + '.key'
            if os.path.isfile(key_file):
                with open(key_file, "rb") as f:
                    self._key = pickle.load(f)
            else:
                self._key = self.generate_valid_key(self.chunk)
                with open(key_file, "wb") as f:
                    pickle.dump(self._key, f)

        # Proper modular inverse
        self.reversed_key = mod_matrix_inv(self._key, 256)

    def generate_valid_key(self, chunk):
        while True:
            key = np.random.randint(0, 256, (chunk, chunk))
            det_val = int(round(det(key))) % 256
            if det_val != 0 and gcd(det_val, 256) == 1:
                return key % 256

    def encode(self, data):
        crypted = []
        for i in range(0, len(data), self.chunk):
            temp = np.dot(self._key, data[i:i + self.chunk]) % 256
            crypted.extend(temp)
        return np.array(crypted, dtype=np.uint8)

    def decode(self, data):
        uncrypted = []
        for i in range(0, len(data), self.chunk):
            temp = np.dot(self.reversed_key, data[i:i + self.chunk]) % 256
            uncrypted.extend(temp)
        return np.array(uncrypted, dtype=np.uint8)
    
    def compute_chunk(self):
        # Use a fixed chunk size for reliability
        return 3  # Works for most RGB images


def run(mode=None):
    """Image encryption/decryption flow"""

    image_file_name = input("Enter image file name: ")
    if not os.path.isfile(image_file_name):
        print(f"Image file {image_file_name} not found.")
        return

    try:
        img = imageio.imread(image_file_name)
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    original_shape = img.shape
    img_vector = img.reshape(1, -1)
    chunk_size = 3
    if img_vector.shape[1] % chunk_size != 0:
        print(f"Image size {img_vector.shape[1]} is not divisible by chunk size {chunk_size}.")
        return

    if mode == "encode":
        hill = Hill(data=img_vector, file_name=image_file_name, chunk=chunk_size)
        try:
            encoded_vector = hill.encode(img_vector[0])
            encoded_img = encoded_vector.reshape(original_shape)
            encoded_img = np.clip(encoded_img, 0, 255).astype('uint8')

            encoded_name = image_file_name.rsplit('.', 1)[0] + "-encoded.png"
            imageio.imwrite(encoded_name, encoded_img)

            with open(encoded_name + ".pk", "wb") as f:
                pickle.dump(encoded_vector, f)

            print(f"Encoded image saved as {encoded_name}")
        except Exception as e:
            print(f"Encoding failed: {e}")

    elif mode == "decode":
        pk_file = input("Enter the full encoded .pk file name: ")
        if not os.path.isfile(pk_file):
            print(f"Encoded data file {pk_file} not found.")
            return

        encoded_img_file = pk_file.replace(".pk", "")
        if not os.path.isfile(encoded_img_file):
            print(f"Encoded image file {encoded_img_file} not found.")
            return

        img = imageio.imread(encoded_img_file)
        original_shape = img.shape

        key_file = input("Enter the key file path: ")
        if not os.path.isfile(key_file):
            print(f"Key file {key_file} not found.")
            return

        hill = Hill(data=img.reshape(1, -1), file_name=encoded_img_file, key_path=key_file)

        with open(pk_file, "rb") as f:
            loaded_vector = pickle.load(f)

        decoded_vector = hill.decode(loaded_vector)
        decoded_img = decoded_vector.reshape(original_shape)
        decoded_img = np.clip(decoded_img, 0, 255).astype('uint8')

        decoded_name = encoded_img_file.rsplit('.', 1)[0] + "-decoded.png"
        imageio.imwrite(decoded_name, decoded_img)

        print(f"Decoded image saved as {decoded_name}")

    else:
        print("Invalid mode. Please choose 'encode' or 'decode'.")