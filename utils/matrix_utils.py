import numpy as np

def mod_inverse(a, m):
    """Find modular inverse of a under mod m."""
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"No modular inverse for {a} under modulus {m}")

def matrix_mod_inv(matrix, modulus):
    """Find modular inverse of a square matrix under mod m."""
    det = int(round(np.linalg.det(matrix))) % modulus
    det_inv = mod_inverse(det, modulus)

    # Adjugate matrix
    matrix_adj = np.round(det * np.linalg.inv(matrix)).astype(int) % modulus
    return (det_inv * matrix_adj) % modulus
