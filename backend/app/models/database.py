import sqlite3
import os
import json
from .schemas import CameraIn, CameraOut

# Standardize robust absolute paths
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STORAGE_DIR = os.path.join(BACKEND_DIR, "storage")
FRAMES_DIR = os.path.join(STORAGE_DIR, "frames")
CLIPS_DIR = os.path.join(STORAGE_DIR, "clips")
DB_DIR = os.path.join(STORAGE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "app.db")

def init_db():
    os.makedirs(FRAMES_DIR, exist_ok=True)
    os.makedirs(CLIPS_DIR, exist_ok=True)
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Cameras table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cameras (
            camera_id TEXT PRIMARY KEY,
            camera_name TEXT,
            location TEXT,
            status TEXT DEFAULT 'Online'
        )
    ''')
    
    # Memory table for Clarify-once
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            camera_id TEXT,
            timestamp TEXT,
            frame_number INTEGER,
            description TEXT,
            frame_path TEXT,
            clip_path TEXT,
            video_path TEXT,
            embedding TEXT
        )
    ''')
    
    # Check if cameras table is empty, if so seed defaults
    cursor.execute("SELECT COUNT(*) FROM cameras")
    if cursor.fetchone()[0] == 0:
        default_cameras = [
            ("camera_01", "Camera 01", "Intersection 1 - North", "Online"),
            ("camera_02", "Camera 02", "Intersection 1 - East", "Online"),
            ("camera_03", "Camera 03", "Intersection 1 - South", "Online")
        ]
        cursor.executemany(
            "INSERT INTO cameras (camera_id, camera_name, location, status) VALUES (?, ?, ?, ?)",
            default_cameras
        )
    
    conn.commit()
    conn.close()

def get_all_cameras():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT camera_id, camera_name, location, status FROM cameras")
    rows = cursor.fetchall()
    conn.close()
    
    return [CameraOut(camera_id=r[0], camera_name=r[1], location=r[2], status=r[3]) for r in rows]

def add_camera_to_db(cam: CameraIn):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO cameras (camera_id, camera_name, location) VALUES (?, ?, ?)",
        (cam.camera_id, cam.camera_name, cam.location)
    )
    conn.commit()
    conn.close()
