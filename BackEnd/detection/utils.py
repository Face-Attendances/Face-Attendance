import cv2
import numpy as np

class FaceDetector:
    def __init__(self, model_path: str = None):
        # load pre-trained cascade hoặc model của bạn
        self.face_cascade = cv2.CascadeClassifier(model_path or 
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect(self, image_path: str):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        results = []
        for (x, y, w, h) in faces:
            results.append({'x': int(x), 'y': int(y), 'w': int(w), 'h': int(h)})
        return results
    def draw_faces(self, image_path: str, output_path: str):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imwrite(output_path, img)
        return output_path
    