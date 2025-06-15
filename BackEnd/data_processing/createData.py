import os
from pathlib import Path
import shutil
import cv2
from datetime import datetime
import threading

class VideoProcessor:
    def __init__(self, input_file="Storing/Get_videos/input_info.txt", log_dir="BackEnd/data_processing/logs"):
        """Khởi tạo VideoProcessor với các tham số cơ bản"""
        self.input_file = Path(input_file)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Load model phát hiện khuôn mặt
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def log(self, message, student_id=None):
        """Ghi log thông tin vào file log và console"""
        timestamp = datetime.now().strftime("[%d/%m/%Y %H:%M:%S]")
        log_file = self.log_dir / f"{student_id}.log" if student_id else self.log_dir / "general.log"
        
        print(f"{timestamp} {message}")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} {message}\n")

    def read_input(self):
        """Đọc thông tin từ file input_info.txt (ID, Tên, Video)"""
        students_info = []
        if not self.input_file.exists():
            self.log("❌ Không tìm thấy file input_info.txt")
            return []

        with open(self.input_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                try:
                    student_id, student_name, video_path = map(str.strip, line.split(";"))
                    students_info.append((student_id, student_name, video_path))
                except ValueError:
                    self.log(f"❌ Định dạng không đúng cho dòng: {line}", "general")
                    continue
        
        return students_info

    def save_student_info(self, student_id, student_name, video_path, action="append"):
        """Xử lý lưu thông tin sinh viên vào file input_info.txt"""
        students_info = self.read_input()

        if action == "overwrite":
            # Ghi đè file (tất cả dữ liệu sẽ bị ghi lại từ đầu)
            with open(self.input_file, "w", encoding="utf-8") as f:
                f.write(f"{student_id};{student_name};{video_path}\n")
            self.log(f"✅ Thông tin sinh viên {student_name} đã được ghi đè.")
        
        elif action == "skip":
            # Bỏ qua nếu sinh viên đã tồn tại
            for student in students_info:
                if student_id == student[0]:  # Kiểm tra nếu sinh viên đã có trong danh sách
                    self.log(f"❌ Sinh viên {student_name} đã tồn tại, bỏ qua.")
                    return  # Bỏ qua nếu đã tồn tại

            # Nếu không có, thêm mới
            with open(self.input_file, "a", encoding="utf-8") as f:
                f.write(f"{student_id};{student_name};{video_path}\n")
            self.log(f"✅ Thông tin sinh viên {student_name} đã được thêm mới.")
        
        elif action == "append":
            # Thêm mới vào cuối file
            with open(self.input_file, "a", encoding="utf-8") as f:
                f.write(f"{student_id};{student_name};{video_path}\n")
            self.log(f"✅ Thông tin sinh viên {student_name} đã được thêm mới.")

    def validate_video(self, video_path):
        """Kiểm tra video có tồn tại và mở được không"""
        if not Path(video_path).exists():
            self.log(f"❌ Video không tồn tại: {video_path}")
            return False

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            self.log(f"❌ Không thể mở video. Có thể lỗi codec hoặc sai định dạng: {video_path}")
            return False

        self.log(f"✅ Đã mở video thành công: {video_path}")
        return cap

    def save_face(self, frame, student_id, student_name, count):
        """Lưu khuôn mặt đã phát hiện vào thư mục với kích thước 200x200"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Phát hiện khuôn mặt
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        # Nếu phát hiện khuôn mặt
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                # Cắt khuôn mặt từ ảnh
                face = frame[y:y+h, x:x+w]
                
                # Resize khuôn mặt về kích thước 200x200
                face_resized = cv2.resize(face, (200, 200))
                
                # Tạo thư mục cho sinh viên nếu chưa có
                student_folder = Path(f"Storing/Get_images/{student_id}_{student_name}")
                student_folder.mkdir(parents=True, exist_ok=True)
                
                # Lưu ảnh khuôn mặt vào thư mục với tên là 'ID_Họ và Tên_{count}.jpg'
                image_path = student_folder / f"{student_id}_{student_name}_{count}.jpg"
                cv2.imwrite(str(image_path), face_resized)
                self.log(f"✅ Lưu ảnh khuôn mặt: {image_path}", student_id)
                return True  # Sau khi lưu một ảnh thì return ngay

        return False  # Không tìm thấy khuôn mặt

    def process_video(self, student_id, student_name, video_path):
        """Xử lý video, phát hiện khuôn mặt và lưu ảnh"""
        cap = self.validate_video(video_path)
        if not cap:
            return

        frame_count = 0
        saved_count = 0
        self.log(f"▶️ Đang đọc từng frame video cho {student_name} - ID: {student_id}", student_id)

        while True:
            ret, frame = cap.read()
            if not ret:
                self.log(f"📉 Kết thúc video hoặc không đọc được frame cho {student_name} - ID: {student_id}", student_id)
                break

            frame_count += 1
            # Lưu ảnh khuôn mặt từ video
            if self.save_face(frame, student_id, student_name, saved_count + 1):
                saved_count += 1

            # Dừng nếu đã đủ ảnh (ví dụ: 30 ảnh)
            if saved_count >= 5:
                self.log(f"✅ Đã lưu đủ 30 ảnh cho sinh viên {student_name} - ID: {student_id}.", student_id)
                break

        cap.release()
        cv2.destroyAllWindows()
        self.log(f"✅ Đã lưu {saved_count} khuôn mặt từ video cho {student_name} - ID: {student_id}", student_id)

    def save_video(self, student_id, student_name, video_path):
        """Sao chép video vào thư mục 'Storing/Get_videos' với tên thư mục là mã số sinh viên và tên"""
        folder_name = f"{student_id}_{student_name}"
        destination_folder = Path(f"Storing/Get_videos/{folder_name}")
        
        # Kiểm tra nếu thư mục con đã tồn tại
        if destination_folder.exists():
            self.log(f"❌ Thư mục {folder_name} đã tồn tại, bỏ qua video.", student_id)
            return  # Bỏ qua nếu thư mục đã tồn tại, không sao chép video
        else:
            destination_folder.mkdir(parents=True, exist_ok=True)
            self.log(f"✅ Tạo thư mục {folder_name} thành công.", student_id)
        
        video_filename = Path(video_path).name  # Lấy tên file video
        new_video_path = destination_folder / video_filename
        
        try:
            shutil.copy(video_path, new_video_path)  # Sao chép video vào thư mục
            self.log(f"✅ Video đã được sao chép vào: {new_video_path}", student_id)
        except Exception as e:
            self.log(f"❌ Đã xảy ra lỗi khi sao chép video: {e}", student_id)

    def run(self):
        """Chạy quá trình xử lý video cho tất cả video trong thư mục Storing/Get_videos"""
        videos_processed = 0
        students_info = self.read_input()

        # Tiến hành xử lý video cho từng sinh viên (tạo luồng xử lý riêng cho mỗi sinh viên)
        threads = []
        for student_id, student_name, video_path in students_info:
            thread = threading.Thread(target=self.process_video, args=(student_id, student_name, video_path))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()  # Chờ tất cả các luồng hoàn thành

        self.log("✅ Hoàn thành xử lý tất cả viideo.", "general")

if __name__ == "__main__":
    processor = VideoProcessor(input_file="BackEnd/data_processing/input_info.txt")
    processor.run()
