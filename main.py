"""
main.py - Entry point. Webcam runs in background thread, Flask on main thread.
Open http://localhost:5000 in browser after running.
Press Q in webcam window to stop.
"""
import cv2
import time
import threading
from datetime import datetime

from face_recognizer import (load_detector, detect_faces,
                              load_known_faces, recognize_face_fr)
from tracker import AttendanceTracker
from csv_logger import save_attendance
from dashboard import create_app

WEBCAM_INDEX      = 0
DETECTION_SCALE   = 0.5
EXIT_CHECK_INTERVAL = 1.0
UNKNOWN_TOLERANCE = 10
FONT              = cv2.FONT_HERSHEY_SIMPLEX
COLOR_INSIDE      = (50, 200, 50)
COLOR_OUTSIDE     = (50, 50, 200)
COLOR_UNKNOWN     = (180, 180, 180)

tracker      = AttendanceTracker()
frame_lock   = threading.Lock()
latest_frame = [None]


def draw_overlay(frame, faces_data):
    for (x, y, w, h, name, status, dist) in faces_data:
        color = COLOR_UNKNOWN if name == "Unknown" else (
            COLOR_INSIDE if status == "INSIDE" else COLOR_OUTSIDE
        )
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        label = f"{name} [{status}]"
        (lw, lh), _ = cv2.getTextSize(label, FONT, 0.55, 1)
        cv2.rectangle(frame, (x, y-lh-10), (x+lw+4, y), color, -1)
        cv2.putText(frame, label, (x+2, y-4), FONT, 0.55, (255,255,255), 1)
    return frame


def webcam_loop():
    print("[INIT] Loading known faces — please wait...\n")
    known_encodings, known_names = load_known_faces("data/registered")

    if not known_encodings:
        print("[ERROR] No faces encoded. Run setup.py first.")
        return

    detector = load_detector()
    cap = cv2.VideoCapture(WEBCAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print(f"[ERROR] Cannot open webcam index {WEBCAM_INDEX}")
        return

    print("[INFO] Webcam running. Press Q to stop.\n")

    label_memory    = {}
    last_exit_check = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        now   = datetime.now()
        small = cv2.resize(frame, (0,0), fx=DETECTION_SCALE, fy=DETECTION_SCALE)
        raw_faces = detect_faces(small, detector)
        inv = 1.0 / DETECTION_SCALE

        faces = [(int(x*inv), int(y*inv), int(w*inv), int(h*inv))
                 for (x,y,w,h) in raw_faces]

        recognised_this_frame = []
        faces_data = []

        for (x, y, w, h) in faces:
            m  = int(0.1 * w)
            x1 = max(0, x-m);  y1 = max(0, y-m)
            x2 = min(frame.shape[1], x+w+m)
            y2 = min(frame.shape[0], y+h+m)
            crop = frame[y1:y2, x1:x2]

            name, dist = recognize_face_fr(crop, known_encodings, known_names)

            slot = (x // 100, y // 100)
            if name != "Unknown":
                label_memory[slot] = {"name": name, "unk": 0}
            else:
                if slot in label_memory:
                    label_memory[slot]["unk"] += 1
                    if label_memory[slot]["unk"] <= UNKNOWN_TOLERANCE:
                        name = label_memory[slot]["name"]
                    else:
                        del label_memory[slot]

            recognised_this_frame.append(name)
            status = tracker.get_status(name)
            faces_data.append((x, y, w, h, name, status, dist))

        tracker.update(recognised_this_frame, now=now)

        cur = time.time()
        if cur - last_exit_check >= EXIT_CHECK_INTERVAL:
            tracker.check_all_exits(now=now)
            last_exit_check = cur

        display = draw_overlay(frame.copy(), faces_data)
        hud = f"{now.strftime('%H:%M:%S')}  |  Faces: {len(faces)}"
        cv2.putText(display, hud, (12,28), FONT, 0.7, (255,255,255), 2)
        cv2.putText(display, hud, (12,28), FONT, 0.7, (30,30,30), 1)

        with frame_lock:
            latest_frame[0] = display.copy()

        cv2.imshow("Smart Attendance", display)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    tracker.check_all_exits(now=datetime.now())
    save_attendance(tracker)
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Webcam stopped.")


if __name__ == "__main__":
    cam_thread = threading.Thread(target=webcam_loop, daemon=True)
    cam_thread.start()

    app = create_app(tracker, latest_frame, frame_lock)
    print("\n[DASHBOARD] Open http://localhost:5000 in your browser\n")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)