"""
csv_logger.py - Saves attendance to timestamped CSV.
"""
import csv
import os
from datetime import datetime

REQUIRED_SECONDS = 30  # 30 seconds for demo. Change to 2400 for production.


def save_attendance(tracker, output_dir="attendance_logs"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename  = os.path.join(output_dir, f"attendance_{timestamp}.csv")

    rows = []
    for p in tracker.all_records():
        rows.append({
            "Name":                 p.name,
            "Entry Time":           p.entry_time.strftime("%H:%M:%S") if p.entry_time else "N/A",
            "Exit Time":            p.exit_time.strftime("%H:%M:%S")  if p.exit_time  else "Still inside",
            "Total Duration (min)": p.duration_minutes(),
            "Attendance":           p.attendance_decision(REQUIRED_SECONDS),
        })

    if not rows:
        print("[INFO] No records to save.")
        return None

    fields = ["Name", "Entry Time", "Exit Time", "Total Duration (min)", "Attendance"]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[SAVED] {filename}")
    print(f"{'Name':<20} {'Duration':>10} {'Result':>10}")
    print("-" * 44)
    for r in rows:
        print(f"{r['Name']:<20} "
              f"{str(r['Total Duration (min)'])+' min':>10} "
              f"{r['Attendance']:>10}")
    return filename