import httpx
import asyncio
import time
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
VIDEO_PATH = Path(r"c:\Users\logit\Downloads\24hr-ku\backend\dummy_test.mp4")

async def run_e2e():
    print("Starting E2E Validation...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Health check
        print("Checking health...")
        resp = await client.get(f"{BASE_URL}/api/health/services")
        print("Health:", resp.json())
        
        # 2. Create camera
        print("Creating camera...")
        resp = await client.post(f"{BASE_URL}/api/cameras", json={
            "name": "Main Gate E2E",
            "location": "Main Gate"
        })
        assert resp.status_code == 200, f"Failed to create camera: {resp.text}"
        camera_id = resp.json()["id"]
        print(f"Camera created: {camera_id}")
        
        # 3. Upload footage
        print("Uploading footage...")
        with open(VIDEO_PATH, "rb") as f:
            files = {"file": ("dummy_test.mp4", f, "video/mp4")}
            data = {
                "camera_id": camera_id,
                "capture_start_utc": datetime.now(timezone.utc).isoformat()
            }
            resp = await client.post(f"{BASE_URL}/api/footage", data=data, files=files)
            assert resp.status_code == 200, f"Upload failed: {resp.text}"
            job_id = resp.json()["job_id"]
            print(f"Job created: {job_id}")
            
        # 4. Poll job status
        print("Polling job status...")
        while True:
            resp = await client.get(f"{BASE_URL}/api/jobs/{job_id}")
            status = resp.json()["status"]
            print(f"Status: {status}")
            if status in ["COMPLETED", "FAILED"]:
                break
            await asyncio.sleep(2)
            
        assert status == "COMPLETED", "Processing job failed"
        
        # 5. Natural Language Query
        print("Executing query...")
        resp = await client.post(f"{BASE_URL}/api/intelligence/query", json={
            "query": "Did a red car pass through the main gate?",
            "camera_ids": [camera_id]
        })
        print("Query response:", resp.json())
        
        print("E2E Validation Complete.")

if __name__ == "__main__":
    asyncio.run(run_e2e())
