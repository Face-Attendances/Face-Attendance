from django.core.management.base import BaseCommand
from pathlib import Path
from detection.services import AttendanceRunner
from django.conf import settings

class Command(BaseCommand):
    help = "Chạy face-attendance từ webcam"

    def handle(self, *args, **opts):
        enc = Path(settings.BASE_DIR) / "Training" / "encodings.pickle"
        imgs= Path(settings.BASE_DIR) / "Storing"  / "Get_images"
        csv = Path(settings.BASE_DIR) / "Database" / "dihoc.csv"

        runner = AttendanceRunner(
            enc_path=enc,
            images_dir=imgs,
            csv_path=csv,
            threshold=0.5,
        )
        runner.run()