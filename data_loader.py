"""
data_loader.py
--------------
Loads registered face images from:
    data/registered/<person_name>/image.jpg

For each person, reads the image, converts to grayscale,
resizes to a fixed size, and flattens into a 1-D vector.            
This vector is used for distance-based face recognition.
"""

import os
import cv2
import numpy as np

# Fixed size all face images will be resized to before comparison
FACE_SIZE = (100, 100)


def load_dataset(dataset_path="data/registered"):
    """
    Walks the dataset directory and loads all registered faces.

    Returns:
        known_encodings : list of np.ndarray  (flattened grayscale face vectors)
        known_names     : list of str         (person name for each encoding)
    """
    known_encodings = []
    known_names = []

    if not os.path.exists(dataset_path):
        print(f"[ERROR] Dataset folder not found: {dataset_path}")
        return known_encodings, known_names

    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        if not os.path.isdir(person_folder):
            continue

        for filename in os.listdir(person_folder):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            img_path = os.path.join(person_folder, filename)
            img = cv2.imread(img_path)

            if img is None:
                print(f"[WARN] Could not read image: {img_path}")
                continue

            encoding = encode_face(img)
            if encoding is not None:
                known_encodings.append(encoding)
                known_names.append(person_name)
                print(f"[INFO] Loaded: {person_name} ({filename})")

    print(f"[INFO] Dataset loaded: {len(known_names)} registered face(s).")
    return known_encodings, known_names


def encode_face(face_img):
    """
    Converts a face image (BGR or grayscale) into a normalised 1-D vector.

    Steps:
        1. Convert to grayscale
        2. Resize to FACE_SIZE (fixed 100×100)
        3. Equalise histogram (improves tolerance to lighting)
        4. Flatten to 1-D and normalise to unit length

    Returns:
        np.ndarray of shape (10000,) or None on failure
    """
    try:
        if len(face_img.shape) == 3:
            gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = face_img

        resized = cv2.resize(gray, FACE_SIZE)
        equalized = cv2.equalizeHist(resized)          # lighting normalisation
        flat = equalized.flatten().astype(np.float32)

        norm = np.linalg.norm(flat)
        if norm == 0:
            return None
        return flat / norm                              # unit vector

    except Exception as e:
        print(f"[ERROR] encode_face failed: {e}")
        return None