from django.core.management.base import BaseCommand
from training.services import train_model

class Command(BaseCommand):
    help = "Train face encodings từ thư mục ảnh và lưu vào encodings.pickle"

    def handle(self, *args, **options):
        count = train_model()
        if count:
            self.stdout.write(self.style.SUCCESS(f"✔ Đã train {count} faces"))
        else:
            self.stdout.write(self.style.WARNING("⚠ Không có khuôn mặt nào được train"))