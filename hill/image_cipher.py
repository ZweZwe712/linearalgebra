import os
import pickle
import numpy as np
import imageio.v2 as imageio
from numpy.linalg import inv, det


class Hill:
    def __init__(self, data, file_name, key_path=None):
        self.data = data
        self.chunk = self.compute_chunk()

        # Load or generate key
        if key_path:
            with open(key_path, "rb") as f:
                self._key = pickle.load(f)
            print(f'Using the args -k {key_path}')
        else:
            key_file = file_name + '.key'
            if os.path.isfile(key_file):
                with open(key_file, "rb") as f:
                    self._key = pickle.load(f)
                print(f'Using the {key_file}')
            else:
                self._key = self.generate_valid_key(self.chunk)
                with open(key_file, "wb") as f:
                    pickle.dump(self._key, f)

        # Inverse key
        self.reversed_key = inv(self._key)

    def compute_chunk(self):
        max_chunk = 100
        data_shape = self.data.shape[1]
        for i in range(max_chunk, 0, -1):
            if data_shape % i == 0:
                return i

    def generate_valid_key(self, chunk):
        while True:
            key = np.random.randint(0, 101, (chunk, chunk))
            if det(key) != 0:
                return key

    @property
    def key(self):
        return self._key

    def encode(self, data):
        """Encrypt using Hill Cipher"""
        crypted = []
        for i in range(0, len(data), self.chunk):
            temp = np.dot(self._key, data[i:i + self.chunk])
            crypted.extend(temp)
        return np.array(crypted)

    def decode(self, data):
        """Decrypt using Hill Cipher"""
        uncrypted = []
        for i in range(0, len(data), self.chunk):
            temp = np.dot(self.reversed_key, data[i:i + self.chunk])
            uncrypted.extend(temp)
        return np.array(uncrypted)


def run():
    """Image encryption/decryption flow"""

    image_file_name = input("Enter image file name: ")

    # Load image
    img = imageio.imread(image_file_name)
    original_shape = img.shape
    img_vector = img.reshape(1, -1)

    # Hill cipher setup
    hill = Hill(data=img_vector, file_name=image_file_name)

    # ---------------- Encode ----------------
    encoded_vector = hill.encode(img_vector[0])
    encoded_img = encoded_vector.reshape(original_shape)
    encoded_img = np.clip(encoded_img, 0, 255).astype('uint8')

    encoded_name = image_file_name.rsplit('.', 1)[0] + "-encoded.png"
    imageio.imwrite(encoded_name, encoded_img)

    with open(encoded_name + ".pk", "wb") as f:
        pickle.dump(encoded_vector, f)

    print(f"Encoded image saved as {encoded_name}")

    # ---------------- Decode ----------------
    with open(encoded_name + ".pk", "rb") as f:
        loaded_vector = pickle.load(f)

    decoded_vector = hill.decode(loaded_vector)
    decoded_img = decoded_vector.reshape(original_shape)
    decoded_img = np.clip(decoded_img, 0, 255).astype('uint8')

    decoded_name = image_file_name.rsplit('.', 1)[0] + "-decoded.png"
    imageio.imwrite(decoded_name, decoded_img)

    print(f"Decoded image saved as {decoded_name}")
