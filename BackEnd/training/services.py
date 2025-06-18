from django.conf import settings
from pathlib import Path
import pickle, cv2, face_recognition

DATA_DIR = Path(settings.CAPTURED_IMAGES_DIR)
OUTPUT_ENCODINGS = Path(settings.OUTPUT_ENCODINGS_FILE)
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp'}

def train_model():
    if not DATA_DIR.is_dir():
        print(f"[ERROR] Không tìm thấy thư mục ảnh: {DATA_DIR}")
        return 0

    known_encodings, known_labels = [], []

    for person_dir in DATA_DIR.iterdir():
        if not person_dir.is_dir(): continue
        label = person_dir.name
        for img_path in person_dir.iterdir():
            if img_path.suffix.lower() not in IMAGE_EXTS: continue
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"[WARN] Không đọc được ảnh: {img_path}")
                continue
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            if not boxes:
                print(f"[WARN] Không phát hiện khuôn mặt: {img_path}")
                continue
            encs = face_recognition.face_encodings(rgb, boxes)
            for e in encs:
                known_encodings.append(e)
                known_labels.append(label)
            print(f"[INFO] Đã mã hóa: {img_path.name} → {label}")

    OUTPUT_ENCODINGS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_ENCODINGS, "wb") as f:
        pickle.dump({"encodings": known_encodings, "labels": known_labels}, f)

    total = len(known_encodings)
    print(f"[DONE] Số khuôn mặt được train: {total}" if total else "[WARN] Không có khuôn mặt nào được train!")
    return total
