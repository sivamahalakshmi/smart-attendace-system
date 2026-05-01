import cv2
import os
import numpy as np

HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
FACE_SIZE = (100, 100)
DATASET   = "data/registered"

detector   = cv2.CascadeClassifier(HAAR_PATH)
recognizer = cv2.face.LBPHFaceRecognizer_create()

faces     = []
labels    = []
label_map = {}
current_label = 0

for person_name in os.listdir(DATASET):
    person_folder = os.path.join(DATASET, person_name)
    if not os.path.isdir(person_folder):
        continue
    label_map[current_label] = person_name
    for filename in os.listdir(person_folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        img = cv2.imread(os.path.join(person_folder, filename), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        img = cv2.resize(img, FACE_SIZE)
        img = cv2.equalizeHist(img)
        faces.append(img)
        labels.append(current_label)
    current_label += 1

recognizer.train(faces, np.array(labels))
print(f"Trained on {len(faces)} images, {len(label_map)} people")
print("Label map:", label_map)
print("\nOpening webcam — look at the CONFIDENCE score printed in terminal...")
print("Lower confidence = better match. Should be below 80 for your face.\n")

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_detected = detector.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))

    for (x, y, w, h) in faces_detected:
        face_crop = gray[y:y+h, x:x+w]
        face_crop = cv2.resize(face_crop, FACE_SIZE)
        face_crop = cv2.equalizeHist(face_crop)

        label, confidence = recognizer.predict(face_crop)
        name = label_map.get(label, "Unknown")

        # Print confidence every frame so you can see the actual number
        print(f"Best match: {name}  |  Confidence: {confidence:.1f}")

        text = f"{name} ({confidence:.0f})"
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

    cv2.imshow("Diagnostic", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()