# detection/services.py

import cv2, face_recognition, csv
import numpy as np
from pathlib import Path
from datetime import datetime
from .utils import EncodingStore

class AttendanceRunner:
    def __init__(
        self,
        enc_path: Path,
        images_dir: Path,
        csv_path: Path,
        threshold: float = 0.5,
        camera_index: int = 0,
    ):
        # Các đường dẫn
        self.store = EncodingStore(enc_path)
        self.images_dir = images_dir
        self.csv_path = csv_path
        self.threshold = threshold
        self.recorded = set()

        # Chuẩn bị các folder/file
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.csv_path.exists():
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["Name", "Time"])

        # Mở webcam
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError(f"Không mở được webcam (index={camera_index})")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def run(self):
        print("Nhấn 'q' để dừng.")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            self._process_frame(frame)
            cv2.imshow("Attendance", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()

    def _process_frame(self, frame):
        # Resize + convert
        small = cv2.resize(frame, (0, 0), fx=0.125, fy=0.125)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

        # Detect + encode
        locs = face_recognition.face_locations(rgb, model="hog")
        encs = face_recognition.face_encodings(rgb, locs)

        for enc, (top, right, bottom, left) in zip(encs, locs):
            name = self._identify(enc)
            # Chỉ lưu lần đầu mỗi người
            if name not in self.recorded:
                self.recorded.add(name)
                self._save_image(frame, name)
                self._log_attendance(name)
            # Vẽ khung
            cv2.rectangle(
                frame,
                (left*8, top*8),
                (right*8, bottom*8),
                (0,255,0), 2
            )
            cv2.putText(
                frame, name,
                (left*8, top*8-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1
            )

    def _identify(self, enc):
        if not self.store.encodings:
            return "Unknown"
        dists = face_recognition.face_distance(self.store.encodings, enc)
        idx   = np.argmin(dists)
        if dists[idx] < self.threshold:
            return self.store.labels[idx]
        # thêm face mới
        label = input("Nhập tên cho khuôn mặt mới: ").strip() \
                or f"Person_{len(self.store.labels)+1}"
        self.store.encodings.append(enc)
        self.store.labels.append(label)
        self.store.save()
        return label

    def _save_image(self, frame, name: str):
        person_dir = self.images_dir / name
        person_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = person_dir / f"Checkin_{ts}.jpg"
        cv2.imwrite(str(path), frame)

    def _log_attendance(self, name: str):
        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
