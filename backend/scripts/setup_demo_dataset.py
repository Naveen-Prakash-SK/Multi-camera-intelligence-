import os
import json
import sys
import cv2
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# We are targeting the AI City Challenge (CityFlow) dataset.
# The dataset requires a signed access agreement, so we cannot automate the download.
DATASET_SOURCE = "https://www.aicitychallenge.org/ai-city-challenge-dataset-access/"
REQUIRED_FILES = {
    "camera_01.mp4": "CityFlow / c001.mp4 (or any real traffic camera video)",
    "camera_02.mp4": "CityFlow / c002.mp4",
    "camera_03.mp4": "CityFlow / c003.mp4"
}

# Real locations corresponding to CityFlow cameras
CAMERAS_META = {
    "camera_01": {
        "name": "Camera 01",
        "location": "Intersection 1 - North"
    },
    "camera_02": {
        "name": "Camera 02",
        "location": "Intersection 1 - East"
    },
    "camera_03": {
        "name": "Camera 03",
        "location": "Intersection 1 - South"
    }
}

def setup_dataset():
    print("Setting up AI City Challenge / CityFlow Dataset...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    missing_files = []
    
    # 1. Check if dataset exists
    for filename in REQUIRED_FILES.keys():
        file_path = DATA_DIR / filename
        if not file_path.exists():
            missing_files.append(filename)
            
    if missing_files:
        print("\n[!] DATASET MISSING [!]")
        print("Because the AI City Challenge dataset requires a signed access agreement, it cannot be downloaded automatically.")
        print(f"Official download/access page: {DATASET_SOURCE}")
        print("\nPlease follow these manual steps:")
        print("1. Gain access to the CityFlow dataset.")
        print("2. Locate the videos for cameras c001, c002, and c003.")
        print(f"3. Rename and place them exactly here:")
        for missing in missing_files:
            print(f"   - {DATA_DIR / missing}")
        print("\nThen run this script again.")
        sys.exit(1)
        
    print("\nDataset found! Verifying files...")
    
    # Verify videos can be opened with OpenCV
    for filename in REQUIRED_FILES.keys():
        file_path = DATA_DIR / filename
        cap = cv2.VideoCapture(str(file_path))
        if not cap.isOpened():
            print(f"[!] Error: OpenCV could not open {file_path}")
            sys.exit(1)
        
        # Read a frame to be absolutely sure
        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"[!] Error: {file_path} seems to be empty or corrupted.")
            sys.exit(1)
            
        cap.release()
        print(f"  [OK] {filename} is a valid video.")
        
    # Create/update camera metadata
    meta_path = DATA_DIR / "cameras.json"
    with open(meta_path, "w") as f:
        json.dump(CAMERAS_META, f, indent=2)
        
    print("\n[OK] metadata created: cameras.json")
    
    # Register cameras in SQLite DB
    import sqlite3
    db_dir = BASE_DIR / "storage" / "db"
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / "app.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cameras (
            camera_id TEXT PRIMARY KEY,
            camera_name TEXT,
            location TEXT,
            status TEXT DEFAULT 'Online'
        )
    ''')
    
    for cam_id, meta in CAMERAS_META.items():
        cursor.execute(
            "INSERT OR REPLACE INTO cameras (camera_id, camera_name, location) VALUES (?, ?, ?)",
            (cam_id, meta["name"], meta["location"])
        )
    
    conn.commit()
    conn.close()
    
    print("[OK] Cameras registered in SQLite database.")
    print("\n[SUCCESS] Dataset setup complete. You can now run the indexing process.")

if __name__ == "__main__":
    setup_dataset()
