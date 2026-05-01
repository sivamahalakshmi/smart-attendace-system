"""
dashboard.py - Flask live attendance dashboard.
Routes:
  /            - main UI
  /video_feed  - MJPEG webcam stream
  /api/data    - JSON attendance data
"""
import time
import cv2
from flask import Flask, Response, jsonify, render_template_string

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Smart Attendance System</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; min-height: 100vh; }
    header { background: #1a1d27; padding: 18px 32px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #2a2d3a; }
    header h1 { font-size: 20px; font-weight: 600; color: #ffffff; }
    .live-badge { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #4ade80; }
    .live-dot { width: 8px; height: 8px; background: #4ade80; border-radius: 50%; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
    .container { max-width: 1200px; margin: 0 auto; padding: 28px 24px; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 24px; }
    .stat-card { background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 12px; padding: 20px; text-align: center; }
    .stat-value { font-size: 32px; font-weight: 700; margin-bottom: 4px; }
    .stat-label { font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; }
    .val-total { color: #60a5fa; } .val-present { color: #4ade80; } .val-absent { color: #f87171; }
    .grid { display: grid; grid-template-columns: 1fr 420px; gap: 24px; align-items: start; }
    .card { background: #1a1d27; border: 1px solid #2a2d3a; border-radius: 12px; overflow: hidden; }
    .card-header { padding: 16px 20px; border-bottom: 1px solid #2a2d3a; font-size: 13px; font-weight: 600; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.8px; }
    .feed-wrapper { padding: 16px; }
    #live-feed { width: 100%; border-radius: 8px; display: block; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    thead th { padding: 12px 16px; text-align: left; font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.6px; border-bottom: 1px solid #2a2d3a; }
    tbody tr { border-bottom: 1px solid #1e2130; transition: background 0.15s; }
    tbody tr:hover { background: #1e2130; }
    tbody tr:last-child { border-bottom: none; }
    td { padding: 14px 16px; vertical-align: middle; }
    .name-cell { font-weight: 600; color: #e0e0e0; }
    .badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
    .badge-inside { background: rgba(74,222,128,0.12); color: #4ade80; }
    .badge-outside { background: rgba(248,113,113,0.12); color: #f87171; }
    .badge-present { background: rgba(74,222,128,0.12); color: #4ade80; }
    .badge-absent { background: rgba(248,113,113,0.12); color: #f87171; }
    .dot { width: 6px; height: 6px; border-radius: 50%; }
    .dot-green { background: #4ade80; } .dot-red { background: #f87171; }
    .time-cell { color: #9ca3af; font-size: 13px; }
    .dur-cell { color: #60a5fa; font-weight: 600; }
    #last-updated { font-size: 12px; color: #4b5563; padding: 12px 20px; border-top: 1px solid #2a2d3a; }
    .empty-state { text-align: center; padding: 48px 20px; color: #4b5563; font-size: 14px; }
  </style>
</head>
<body>
<header>
  <h1>Smart Attendance System</h1>
  <div class="live-badge"><div class="live-dot"></div>Live</div>
</header>
<div class="container">
  <div class="stats">
    <div class="stat-card"><div class="stat-value val-total" id="s-total">0</div><div class="stat-label">Total Students</div></div>
    <div class="stat-card"><div class="stat-value val-present" id="s-present">0</div><div class="stat-label">Present</div></div>
    <div class="stat-card"><div class="stat-value val-absent" id="s-absent">0</div><div class="stat-label">Absent</div></div>
  </div>
  <div class="grid">
    <div class="card">
      <div class="card-header">Attendance Records</div>
      <div style="overflow-x:auto">
        <table>
          <thead><tr><th>Roll Number</th><th>Status</th><th>Entry</th><th>Exit</th><th>Duration</th><th>Result</th></tr></thead>
          <tbody id="attendance-body">
            <tr><td colspan="6" class="empty-state">Waiting for faces to be detected...</td></tr>
          </tbody>
        </table>
      </div>
      <div id="last-updated">Refreshing every 4 seconds</div>
    </div>
    <div class="card">
      <div class="card-header">Live Camera Feed</div>
      <div class="feed-wrapper"><img id="live-feed" src="/video_feed" alt="Live feed"/></div>
    </div>
  </div>
</div>
<script>
function fetchData() {
  fetch('/api/data').then(r => r.json()).then(data => {
    document.getElementById('s-total').textContent   = data.total;
    document.getElementById('s-present').textContent = data.present;
    document.getElementById('s-absent').textContent  = data.absent;
    const tbody = document.getElementById('attendance-body');
    if (data.records.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-state">Waiting for faces to be detected...</td></tr>';
      return;
    }
    tbody.innerHTML = data.records.map(r => `
      <tr>
        <td class="name-cell">${r.name}</td>
        <td>${r.status === 'INSIDE'
          ? '<span class="badge badge-inside"><div class="dot dot-green"></div>Inside</span>'
          : '<span class="badge badge-outside"><div class="dot dot-red"></div>Outside</span>'}</td>
        <td class="time-cell">${r.entry_time}</td>
        <td class="time-cell">${r.exit_time}</td>
        <td class="dur-cell">${r.duration} min</td>
        <td>${r.attendance === 'PRESENT'
          ? '<span class="badge badge-present">Present</span>'
          : '<span class="badge badge-absent">Absent</span>'}</td>
      </tr>`).join('');
    document.getElementById('last-updated').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
  }).catch(() => {});
}
fetchData();
setInterval(fetchData, 4000);
</script>
</body>
</html>
"""


def create_app(tracker, latest_frame, frame_lock):
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template_string(HTML)

    @app.route("/api/data")
    def api_data():
        records = tracker.snapshot()
        total   = len(records)
        present = sum(1 for r in records if r["attendance"] == "PRESENT")
        return jsonify({"records": records, "total": total,
                        "present": present, "absent": total - present})

    @app.route("/video_feed")
    def video_feed():
        def generate():
            while True:
                with frame_lock:
                    frame = latest_frame[0]
                if frame is None:
                    time.sleep(0.05)
                    continue
                _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
                       jpeg.tobytes() + b"\r\n")
        return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

    return app