import httpx
import uuid
import time
import os

BASE_URL = "http://localhost:8000/api"

def run_tests():
    print("Running E2E Verification Flow for HNX26EPS05...")
    client = httpx.Client(timeout=10.0)

    # 1. Camera Creation
    print("1. Creating camera...")
    cam_data = {
        "name": "Main Gate E2E",
        "description": "Gate facing east",
        "source_type": "file",
        "location": "Entrance"
    }
    r = client.post(f"{BASE_URL}/cameras", json=cam_data)
    r.raise_for_status()
    camera = r.json()
    camera_id = camera["id"]
    print(f"Created Camera: {camera_id}")

    # 2. Scene Memory Persistence
    print("2. Creating scene memory...")
    mem_data = {
        "location_name": f"Main Gate - {uuid.uuid4()}",
        "camera_id": camera_id,
        "aliases": ["entrance", "front gate"]
    }
    r = client.post(f"{BASE_URL}/memory", json=mem_data)
    r.raise_for_status()
    print("Scene memory persisted.")

    # 3. Create a dummy mp4 file
    print("3. Uploading footage...")
    dummy_file = "dummy_test.mp4"
    if not os.path.exists(dummy_file):
        os.system(f"ffmpeg -f lavfi -i color=c=black:s=320x240:d=2 -c:v libx264 {dummy_file} -y >nul 2>&1")

    with open(dummy_file, "rb") as f:
        files = {"file": (dummy_file, f, "video/mp4")}
        data = {
            "camera_id": camera_id,
            "capture_start_utc": "2026-10-08T10:00:00Z"
        }
        r = client.post(f"{BASE_URL}/footage", files=files, data=data)
        r.raise_for_status()
        job = r.json()
        job_id = job["job_id"]
        print(f"Footage uploaded. Job ID: {job_id}")

    # 4. Wait for Job completion
    print("Waiting for job completion...")
    for _ in range(30):
        time.sleep(2)
        r = client.get(f"{BASE_URL}/jobs/{job_id}")
        if r.status_code == 200:
            status = r.json()["status"]
            print(f"Job status: {status}")
            if status == "COMPLETED":
                break
            if status == "FAILED":
                print("Job failed!")
                return
        else:
            print("Job not found yet...")
    
    # 5. Semantic Query
    print("5. Executing Semantic Query...")
    q_data = {
        "query": "person in red clothing at the main gate"
    }
    r = client.post(f"{BASE_URL}/query", json=q_data)
    r.raise_for_status()
    q_res = r.json()
    print(f"Query Result Verdict: {q_res['verdict']}")
    print(f"Results Count: {len(q_res['results'])}")
    
    if len(q_res['results']) > 0:
        print("Success! E2E Flow verified.")
    else:
        print("Warning: Query returned 0 results. Check pipeline logic.")

if __name__ == "__main__":
    run_tests()
