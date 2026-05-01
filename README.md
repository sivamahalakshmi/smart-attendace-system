# Smart Facial Recognition Based Automatic Attendance System

An automated, contactless attendance system that uses computer vision 
to detect and recognize student faces from a live webcam feed and 
logs attendance into a structured CSV file — without any manual 
intervention from students or faculty.

---

## Features

- Real-time face detection using Haar Cascade Classifier
- Face recognition using Euclidean distance comparison
- Appearance-based Entry / Exit tracking
- 40/50 Rule — minimum 40 minutes presence required to be marked Present
- Cooldown mechanism to prevent duplicate entries
- Flask web dashboard accessible at localhost:5000
- Auto-generated CSV attendance logs with timestamps
- Faculty Mode for manual override
- Works on standard hardware with any USB webcam

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Core application logic |
| OpenCV | Face detection and image processing |
| NumPy | Image vector comparison (Euclidean distance) |
| Flask | Web dashboard |
| CSV Module | Structured attendance record storage |
| Webcam | Zebronics ZEB-Ultimate Pro (USB) |

---

## Project Structure
```
smart-attendance-system/
├── data/
│   └── registered/
│       ├── 230101032/       ← Student reference images (by roll number)
│       └── 230101053/
├── attendance_logs/         ← Auto-generated CSV files (gitignored)
├── csv_logger.py            ← CSV generation and 40/50 rule logic
├── dashboard.py             ← Flask web dashboard
├── data_loader.py           ← Dataset loading and vector preparation
├── face_recognizer.py       ← Haar Cascade detection + Euclidean recognition
├── main.py                  ← Main entry point
├── tracker.py               ← Entry/exit appearance tracking
├── setup.py                 ← Environment setup script
├── test_recognition.py      ← Standalone recognition testing script
├── requirements.txt         ← Python dependencies
└── readme.md                ← This file
```

---

## How It Works

1. **Load dataset** — Student reference images are loaded from 
   `data/registered/` and converted to numerical vectors
2. **Start webcam** — Live video feed is captured frame by frame
3. **Detect face** — Haar Cascade Classifier locates face regions 
   in each frame
4. **Recognize face** — Euclidean distance is computed between the 
   detected face and all reference vectors; closest match is identified
5. **Track appearance** — First detection = ENTRY logged, 
   Second detection = EXIT logged
6. **Validate time** — 40/50 Rule applied to compute Present / Absent
7. **Save to CSV** — Final attendance record written to 
   `attendance_logs/`
8. **Dashboard** — Flask app displays live results at localhost:5000

---

## Setup and Installation

### Step 1 — Clone the repository
```bash
git clone https://github.com/sivamahalakshmi/smart-attendance-system.git
cd smart-attendance-system
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Add student images

Create a folder inside `data/registered/` named by the student's 
roll number and add at least 3 photos:
data/registered/
└── 230101001/
├── img_001.jpg
├── img_002.jpg
└── img_003.jpg

### Step 4 — Run the system
```bash
python main.py
```

The webcam will start and the dashboard will be available at 
`http://localhost:5000`

---

## System Requirements

| Component | Minimum | Used in Development |
|---|---|---|
| Processor | Intel Core i3 | Intel Core i5 |
| RAM | 4 GB | 8 GB |
| Camera | Any USB webcam (480p) | Zebronics ZEB-Ultimate Pro |
| OS | Windows 10 / Ubuntu 20.04 | Windows 11 |
| Python | 3.8+ | Python 3.11 |

---

## How Attendance is Logged

Each CSV file in `attendance_logs/` is named by session 
date and time. Example:
attendance_2026-04-15_14-44-52.csv
 | Roll Number | Name | Entry Time | Exit Time | Duration (mins) | Status | Remarks |
|---|---|---|---|---|---|---|
| 230101032 | Nivethitha M | 09:02:14 | 09:51:38 | 49 | Present | — |
| 230101053 | Sivamahalakshmi S | 09:03:45 | 09:48:22 | 44 | Present | — |

---

## Known Limitations

- Performance degrades in low or uneven lighting conditions
- Classical CV approach — less robust than deep learning models
- May confuse students with very similar facial features
- No spoof detection — cannot distinguish real faces from photos

---

## Future Enhancements

- Deep learning integration using FaceNet for higher accuracy
- Multi-camera support for larger classrooms
- Cloud-based attendance storage and reporting
- Liveness detection for anti-spoofing
- Real-time dashboard with attendance trend graphs
- Integration with institutional management systems

---

## Authors

**Nivethitha M** (230101032)  
**Sivamahalakshmi S** (230101053)  
B.E. Aeronautical Engineering  
Rajalakshmi Engineering College, Chennai  
May 2026

---

## Mentor

**Dr. Suresh Chandra Khandai**  
Head of Department & Professor  
Aeronautical Engineering  
Rajalakshmi Engineering College

---

## License

This project was developed as part of the Innovation and Design 
Thinking Lab course. For academic use only.
