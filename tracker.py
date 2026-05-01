"""
tracker.py - Gate-based attendance.
1st appearance = ENTRY, 2nd appearance = EXIT.
Duration = exit_time - entry_time.
"""
from datetime import datetime


class PersonTracker:
    def __init__(self, name, entry_time):
        self.name               = name
        self.entry_time         = entry_time
        self.exit_time          = None
        self.last_seen_time     = entry_time
        self.inside             = True
        self.exited             = False
        self._cooldown_secs     = 30

    def try_exit(self, now):
        if self.exited:
            return False
        if (now - self.entry_time).total_seconds() < self._cooldown_secs:
            return False
        self.exit_time = now
        self.inside    = False
        self.exited    = True
        return True

    def duration_minutes(self):
        if self.exit_time:
            secs = (self.exit_time - self.entry_time).total_seconds()
        else:
            secs = (datetime.now() - self.entry_time).total_seconds()
        return round(secs / 60, 1)

    def status_label(self):
        return "INSIDE" if self.inside else "OUTSIDE"

    def attendance_decision(self, required_secs=2400.0):
        if self.exit_time:
            duration = (self.exit_time - self.entry_time).total_seconds()
        else:
            duration = (datetime.now() - self.entry_time).total_seconds()
        return "PRESENT" if duration >= required_secs else "ABSENT"


class AttendanceTracker:
    def __init__(self):
        self.records = {}

    def update(self, recognised_names, now=None):
        if now is None:
            now = datetime.now()
        for name in recognised_names:
            if name == "Unknown":
                continue
            if name not in self.records:
                self.records[name] = PersonTracker(name, entry_time=now)
                print(f"[ENTRY]  {name} at {now.strftime('%H:%M:%S')}")
            else:
                person = self.records[name]
                if not person.exited:
                    if person.try_exit(now):
                        print(f"[EXIT]   {name} at {now.strftime('%H:%M:%S')} "
                              f"| Duration: {person.duration_minutes()} min")

    def check_all_exits(self, now=None):
        pass

    def get_status(self, name):
        if name in self.records:
            return self.records[name].status_label()
        return "OUTSIDE"

    def all_records(self):
        return list(self.records.values())

    def snapshot(self):
        result = []
        for p in self.records.values():
            result.append({
                "name":       p.name,
                "status":     p.status_label(),
                "entry_time": p.entry_time.strftime("%H:%M:%S") if p.entry_time else "--",
                "exit_time":  p.exit_time.strftime("%H:%M:%S")  if p.exit_time  else "--",
                "duration":   p.duration_minutes(),
                "attendance": p.attendance_decision(),
            })
        return result