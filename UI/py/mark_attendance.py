import csv
import os
import sys

def get_attendance_csv_path():
    # Always use the correct path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, '..', 'Attendance.csv')

def update_attendance_csv(regNo, day, present):
    filename = get_attendance_csv_path()
    print("DEBUG: Writing to", filename)  # Add this line
    rows = []
    day_col = None
    if not os.path.isfile(filename):
        print(f"{filename} not found!")
        return

    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    header = rows[0]
    if day in header:
        day_col = header.index(day)
    else:
        print(f"Day {day} column not found in CSV")
        return

    found = False
    for i in range(1, len(rows)):
        if rows[i][0] == regNo:
            rows[i][day_col] = '1' if present else '0'
            found = True
            break

    if not found:
        # Append new student row
        new_row = [regNo] + ['0'] * (len(header) - 1)
        new_row[day_col] = '1' if present else '0'
        rows.append(new_row)
        print(f"RegNo {regNo} not found. Added new row.")

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(rows)
    print(f"Attendance updated for {regNo} on {day}: {'Present' if present else 'Absent'}")

def mark_attendance(regNo, day, face_score=None, audio_score=None, face_threshold=0.15, audio_threshold=0.5):
    if face_score is None or audio_score is None:
        print("Both face and audio scores are required.")
        return
    present = (face_score >= face_threshold) and (audio_score >= audio_threshold)
    update_attendance_csv(regNo, day, present)

if __name__ == "__main__":
    if len(sys.argv) == 5:
        regNo = sys.argv[1]
        day = sys.argv[2]
        face_score = float(sys.argv[3])
        audio_score = float(sys.argv[4])
        mark_attendance(regNo, day, face_score, audio_score)
    else:
        print("Usage: python mark_attendance.py <regNo> <day> <face_score> <audio_score>")