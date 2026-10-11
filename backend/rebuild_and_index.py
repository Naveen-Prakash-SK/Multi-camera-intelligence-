import os
import shutil
import sqlite3
import time

from app.models.database import init_db, DB_PATH, FRAMES_DIR, CLIPS_DIR, DB_DIR
from app.services.video_processor import process_video_bg

def rebuild_index():
    print("=" * 60)
    print("STARTING COMPLETE DATABASE & INDEX REBUILD")
    print("=" * 60)
    
    # Clean storage directories
    if os.path.exists(FRAMES_DIR):
        shutil.rmtree(FRAMES_DIR)
    if os.path.exists(CLIPS_DIR):
        shutil.rmtree(CLIPS_DIR)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(CLIPS_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Initialize fresh DB
    init_db()
    print("Initialized clean SQLite database and storage directories.")
    
    # Process each video stream synchronously
    videos = [
        ("camera_01", os.path.abspath("data/camera_01.mp4")),
        ("camera_02", os.path.abspath("data/camera_02.mp4")),
        ("camera_03", os.path.abspath("data/camera_03.mp4"))
    ]
    
    for cam_id, vpath in videos:
        print(f"\nProcessing {cam_id} ({vpath})...")
        process_video_bg(cam_id, vpath, interval_seconds=2.0)
        
    # Verify results
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]
    
    cursor.execute("SELECT camera_id, description, COUNT(*) FROM events GROUP BY camera_id, description")
    rows = cursor.fetchall()
    
    print("\n" + "=" * 60)
    print(f"REBUILD COMPLETE: {total_events} events indexed across 3 cameras.")
    print("Breakdown by camera & visual classification:")
    for r in rows:
        print(f"  - [{r[0]}] {r[1]}: {r[2]} frames")
        
    frame_files = os.listdir(FRAMES_DIR)
    print(f"Extracted JPEG frames on disk: {len(frame_files)} in {FRAMES_DIR}")
    print("=" * 60)
    conn.close()

if __name__ == "__main__":
    rebuild_index()
