#!/usr/bin/env python3
# backend/recognition/Face_dt.py

from pathlib import Path
import cv2
import face_recognition
import pickle
import csv
from datetime import datetime
from threading import Thread
from queue import Queue
import numpy as np

# --- Thiết lập đường dẫn --- 
BASE_DIR       = Path(__file__).resolve().parent.parent
ENC_PATH       = BASE_DIR / "Training"    / "encodings.pickle"
INFO_FILE      = BASE_DIR / "Detection"   / "info.txt"
ATTEND_CSV     = BASE_DIR / "Database"    / "dihoc.csv"
SAVE_DIR       = BASE_DIR / "Storing"     / "Get_images"
DIST_THRESHOLD = 0.5

# --- Khởi tạo folder/file nếu cần --- 
INFO_FILE.parent.mkdir(parents=True, exist_ok=True)
INFO_FILE.touch(exist_ok=True)

ATTEND_CSV.parent.mkdir(parents=True, exist_ok=True)
if not ATTEND_CSV.exists():
    with open(ATTEND_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Time"])

SAVE_DIR.mkdir(parents=True, exist_ok=True)

# --- Load encodings cũ --- 
with open(ENC_PATH, "rb") as f:
    data = pickle.load(f)
known_encodings = data.get("encodings", [])
known_labels    = data.get("labels", [])

if not known_encodings:
    print("[ERROR] Chưa có face encodings! Chạy Training.py trước.")  # :contentReference[oaicite:0]{index=0} L31-L34
    exit(1)

# --- Mở webcam và cấu hình --- 
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Không thể mở webcam.")
    exit(1)

# Giới hạn độ phân giải và FPS
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 15)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Nhấn 'q' để thoát.")

# --- Thiết lập multithreading để đọc frame --- 
frame_queue = Queue(maxsize=1)

def capture_thread(q, video_stream):
    while True:
        ret, frame = video_stream.read()
        if not ret:
            break
        if q.full():
            try:
                q.get_nowait()
            except:
                pass
        q.put(frame)
        # cho phép thoát nhanh
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

Thread(target=capture_thread, args=(frame_queue, cap), daemon=True).start()

# --- Vòng lặp xử lý --- 
recorded = set()
frame_count = 0
PROCESS_EVERY_N = 2    # chỉ process mỗi 2 frame

while True:
    if frame_queue.empty():
        continue
    frame = frame_queue.get()
    frame_count += 1

    # Hiển thị luôn frame nếu không đến lượt xử lý
    if frame_count % PROCESS_EVERY_N != 0:
        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # Resize và convert màu
    small_frame = cv2.resize(frame, (0, 0), fx=0.125, fy=0.125)  # chỉ 12.5% kích thước :contentReference[oaicite:1]{index=1} L54-L56
    rgb_small  = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect với model HOG
    face_locations = face_recognition.face_locations(rgb_small, model="hog")
    face_encs      = face_recognition.face_encodings(rgb_small, face_locations)

    for face_enc in face_encs:
        # Tìm k-nearest bằng khoảng cách
        distances = face_recognition.face_distance(known_encodings, face_enc)
        if len(distances) > 0:
            best_idx  = np.argmin(distances)
            if distances[best_idx] < DIST_THRESHOLD:
                name = known_labels[best_idx]
            else:
                name = "Unknown"
        else:
            name = "Unknown"

        if name == "Unknown":
            # Thêm face mới và hỏi tên
            known_encodings.append(face_enc)
            name = input("Nhập tên cho khuôn mặt mới: ").strip() or f"Person_{len(known_labels)+1}"
            known_labels.append(name)
            with open(ENC_PATH, "wb") as f:
                pickle.dump({"encodings": known_encodings, "labels": known_labels}, f)

        # Ghi nhận chỉ 1 lần cho mỗi mặt
        if name not in recorded:
            recorded.add(name)
            print(f"Recognized: {name}")

            # Lưu ảnh gốc với timestamp
            person_dir = SAVE_DIR / name
            person_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = person_dir / f"Checkin_{ts}.jpg"
            cv2.imwrite(str(img_path), frame)

            # Ghi log vào CSV điểm danh
            with open(ATTEND_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    # Hiển thị kết quả
    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng
cap.release()
cv2.destroyAllWindows()
