import cv2
import httpx
import numpy as np

stream_url = "http://127.0.0.1:8001/"

def check_stream():
    print(f"Checking stream at {stream_url}...")
    try:
        # Sometimes direct cv2.VideoCapture works if it's an mjpeg stream without auth
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            print("OpenCV could not open stream directly.")
            # Let's try httpx with headers to see what kind of stream it is
            print("Checking HTTP headers...")
            resp = httpx.get(stream_url, headers={"X-Forwarded-Tunnels-Id": "1"}, timeout=10, verify=False)
            print(f"Status Code: {resp.status_code}")
            print(f"Content-Type: {resp.headers.get('Content-Type')}")
            return
            
        ret, frame = cap.read()
        if ret:
            print(f"Successfully read frame! Shape: {frame.shape}")
        else:
            print("Opened but failed to read frame.")
        cap.release()
    except Exception as e:
        print(f"Error checking stream: {e}")

if __name__ == "__main__":
    check_stream()
