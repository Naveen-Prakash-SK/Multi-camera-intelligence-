import sqlite3
import os
import json
from .schemas import CameraIn, CameraOut

DB_PATH = "storage/db/app.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
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
