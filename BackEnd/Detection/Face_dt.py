# backend/recognition/Face_dt.py

from pathlib import Path
import cv2
import face_recognition
import pickle
import csv
from datetime import datetime

# --- Thiết lập đường dẫn ---
BASE_DIR       = Path(__file__).resolve().parent.parent
ENC_PATH       = BASE_DIR / "Training"    / "encodings.pickle"
INFO_FILE      = BASE_DIR / "Detection" / "info.txt"
ATTEND_CSV     = BASE_DIR / "Database"    / "dihoc.csv"
DIST_THRESHOLD = 0.5
SAVE_DIR = BASE_DIR / "Storing" / "Get_images"

# --- Khởi tạo file if needed ---
INFO_FILE.parent.mkdir(parents=True, exist_ok=True)
INFO_FILE.touch(exist_ok=True)

ATTEND_CSV.parent.mkdir(parents=True, exist_ok=True)
if not ATTEND_CSV.exists():
    with open(ATTEND_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Time"])

SAVE_DIR.mkdir(parents=True, exist_ok=True)

# --- Load encodings ---
with open(ENC_PATH, "rb") as f:
    data = pickle.load(f)
known_encodings = data.get("encodings", [])
known_labels    = data.get("labels", [])

if not known_encodings:
    print("[ERROR] Chưa có face encodings! Chạy Training.py trước.")
    exit(1)

# --- Mở webcam ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Không thể mở webcam.")
    exit(1)

print("Nhấn 'q' để thoát.")

recorded = set()
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_encodings, face_encoding, DIST_THRESHOLD)
        name = "Unknown"

        if True in matches:
            match_index = matches.index(True)
            name = known_labels[match_index]
        else:
            # Add new face to encodings and labels
            known_encodings.append(face_encoding)
            # Nhập tên folder/người dùng thủ công
            name = input("Nhập tên folder/người dùng cho khuôn mặt mới: ").strip()
            if not name:
                name = f"Person_{len(known_labels) + 1}"
            known_labels.append(name)

            # Save new encoding to file
            with open(ENC_PATH, "wb") as f:
                pickle.dump({"encodings": known_encodings, "labels": known_labels}, f)

        if name not in recorded:
            recorded.add(name)
            print(f"Recognized: {name}")

            # Create folder for the person if not exists
            person_dir = SAVE_DIR / name
            person_dir.mkdir(parents=True, exist_ok=True)

            # Save image to the person's folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = person_dir / f"Checkin_{timestamp}.jpg"
            cv2.imwrite(str(image_path), frame)

            # Log attendance
            with open(ATTEND_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    # Display the resulting frame
    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
