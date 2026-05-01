import cv2
import os
import argparse

HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

def capture_faces(name, save_dir="data/registered"):
    person_dir = os.path.join(save_dir, name)
    os.makedirs(person_dir, exist_ok=True)
    detector = cv2.CascadeClassifier(HAAR_PATH)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return
    count = 0
    print(f"\n[INFO] Registering: {name} — Press SPACE to capture, Q to quit\n")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
        display = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(display, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(display, f"Saved: {count}/8 | SPACE=capture Q=quit",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        cv2.imshow(f"Register - {name}", display)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(" ") and count < 8:
            if len(faces) >= 1:
                # Save the FULL FRAME — not a crop, not grayscale
                path = os.path.join(person_dir, f"image_{count+1}.jpg")
                cv2.imwrite(path, frame)
                count += 1
                print(f"[SAVED] {path}")
            else:
                print("[WARN] No face detected.")
        elif key == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[DONE] {count} images saved for {name}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    capture_faces(args.name)