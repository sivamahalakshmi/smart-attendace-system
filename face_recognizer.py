import cv2
import os
import numpy as np
import face_recognition

TOLERANCE = 0.5

def load_detector():
    haar = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(haar)
    print("[INFO] Detector loaded.")
    return detector

def load_known_faces(dataset_path="data/registered"):
    known_encodings = []
    known_names = []
    if not os.path.exists(dataset_path):
        print(f"[ERROR] Path not found: {dataset_path}")
        return [], []
    for person_name in sorted(os.listdir(dataset_path)):
        person_folder = os.path.join(dataset_path, person_name)
        if not os.path.isdir(person_folder):
            continue
        image_files = [f for f in os.listdir(person_folder)
                       if f.lower().endswith((".jpg",".jpeg",".png"))]
        print(f"[INFO] Encoding {person_name} — {len(image_files)} images...")
        encoded = 0
        for filename in image_files:
            img_path = os.path.join(person_folder, filename)
            # Load as full color
            img = face_recognition.load_image_file(img_path)
            # img is now RGB numpy array — find faces in it
            locs = face_recognition.face_locations(img)
            if not locs:
                print(f"       [SKIP] No face found in {filename}")
                continue
            encs = face_recognition.face_encodings(img, locs)
            if encs:
                known_encodings.append(encs[0])
                known_names.append(person_name)
                encoded += 1
        print(f"       {encoded}/{len(image_files)} encoded.")
    print(f"\n[INFO] Total: {len(known_encodings)} encodings, "
          f"{len(set(known_names))} people.\n")
    return known_encodings, known_names

def detect_faces(frame, detector):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80,80))
    return faces.tolist() if len(faces) > 0 else []

def recognize_face_fr(face_crop, known_encodings, known_names):
    if not known_encodings:
        return "Unknown", 1.0
    # Convert BGR to RGB properly
    rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
    # Find face locations within the crop
    locs = face_recognition.face_locations(rgb)
    if not locs:
        return "Unknown", 1.0
    encodings = face_recognition.face_encodings(rgb, locs)
    if not encodings:
        return "Unknown", 1.0
    distances = face_recognition.face_distance(known_encodings, encodings[0])
    best_idx = int(np.argmin(distances))
    best_dist = float(distances[best_idx])
    if best_dist <= TOLERANCE:
        return known_names[best_idx], round(best_dist, 2)
    return "Unknown", round(best_dist, 2)