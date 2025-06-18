
from pathlib import Path
import pickle
import cv2
import face_recognition
from datetime import datetime

class EncodingStore:
    def __init__(self, path: Path):
        self.path = path
        self.encodings, self.labels = self._load()

    def _load(self):
        if not self.path.exists():
            return [], []
        with open(self.path, "rb") as f:
            data = pickle.load(f)
        return data.get("encodings", []), data.get("labels", [])

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "wb") as f:
            pickle.dump({
                "encodings": self.encodings,
                "labels": self.labels
            }, f)

class FaceDetector:
    def __init__(self, model_path: str = None):
        self.face_cascade = cv2.CascadeClassifier(
            model_path or cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def detect(self, image_path: str):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return [{'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)} for x,y,w,h in faces]

    def draw_faces(self, image_path: str, output_path: str):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 2)
        cv2.imwrite(output_path, img)
        return output_path