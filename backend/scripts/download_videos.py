import os
import cv2
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

videos = [
    {"url": "https://github.com/intel-iot-devkit/sample-videos/raw/master/car-detection.mp4", "filename": "camera_01.mp4"},
    {"url": "https://github.com/intel-iot-devkit/sample-videos/raw/master/person-bicycle-car-detection.mp4", "filename": "camera_02.mp4"},
    {"url": "https://github.com/intel-iot-devkit/sample-videos/raw/master/head-pose-face-detection-female-and-male.mp4", "filename": "camera_03.mp4"}
]

def download_videos():
    for v in videos:
        filepath = DATA_DIR / v["filename"]
        if filepath.exists() and os.path.getsize(filepath) > 0:
            print(f"{v['filename']} already exists.")
            continue
            
        print(f"Downloading {v['filename']} from {v['url']}...")
        cmd = ["curl.exe", "--ssl-no-revoke", "-L", v["url"], "-o", str(filepath)]
        subprocess.run(cmd, check=True)

def verify_and_print():
    for v in videos:
        filepath = DATA_DIR / v["filename"]
        cap = cv2.VideoCapture(str(filepath))
        if not cap.isOpened():
            print(f"{v['filename']}: OpenCV failed to open.")
            continue
            
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        duration = frame_count / fps if fps > 0 else 0
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        file_size = os.path.getsize(filepath) / (1024 * 1024)
        
        print(f"--- {v['filename']} ---")
        print(f"Resolution: {int(width)}x{int(height)}")
        print(f"FPS: {fps:.2f}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"File Size: {file_size:.2f} MB")
        print("Status: Verified with OpenCV")
        print("")
        cap.release()

if __name__ == "__main__":
    download_videos()
    verify_and_print()
