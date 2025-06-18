import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'attendance.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def import_from_csv(csv_path: str):
    import csv
    conn = get_connection()
    cur = conn.cursor()
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO database_attendance (user_id, timestamp, present) VALUES (?, ?, ?)",
                (row['user_id'], row['timestamp'], row['present'])
            )
    conn.commit()
    conn.close()
