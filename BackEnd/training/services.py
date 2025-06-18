from pathlib import Path
import pickle
import cv2
import face_recognition

# --- Thiết lập đường dẫn ---
BASE_DIR         = Path(__file__).resolve().parent.parent
DATA_DIR         = BASE_DIR / "Storing" / "Get_images"
OUTPUT_ENCODINGS = BASE_DIR / "Training" / "encodings.pickle"
IMAGE_EXTS       = {".jpg", ".jpeg", ".png", ".bmp"}

def train_encodings():
    if not DATA_DIR.is_dir():
        print(f"[ERROR] Không tìm thấy thư mục ảnh: {DATA_DIR}")
        return 0

    known_encodings = []
    known_labels    = []

    for person_dir in DATA_DIR.iterdir():
        if not person_dir.is_dir():
            continue
        label = person_dir.name
        for img_path in person_dir.iterdir():
            if img_path.suffix.lower() not in IMAGE_EXTS:
                continue
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"[WARN] Không đọc được ảnh: {img_path}")
                continue
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            if not boxes:
                print(f"[WARN] Không phát hiện khuôn mặt: {img_path}")
                continue
            encodings = face_recognition.face_encodings(rgb, boxes)
            for encoding in encodings:
                known_encodings.append(encoding)
                known_labels.append(label)
            print(f"[INFO] Đã mã hóa: {img_path.name} → {label}")

    OUTPUT_ENCODINGS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_ENCODINGS, "wb") as f:
        pickle.dump({"encodings": known_encodings, "labels": known_labels}, f)

    total = len(known_encodings)
    if total:
        print(f"[DONE] Số khuôn mặt được train: {total}")
    else:
        print("[WARN] Không có khuôn mặt nào được train!")
    return total
if __name__ == "__main__":
    total_faces = train_encodings()
    if total_faces > 0:
        print(f"Đã train thành công {total_faces} khuôn mặt.")
    else:
        print("Không có khuôn mặt nào được train.")