import httpx
import asyncio
import time
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
VIDEO_PATH = Path(r"c:\Users\logit\Downloads\24hr-ku\dummy_test.mp4")

async def run_benchmark():
    print("Starting E2E Benchmark and Validation...")
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Health check
        print("\n--- 1. Health Check ---")
        try:
            resp = await client.get(f"{BASE_URL}/api/health/services")
            print("Health:", resp.json())
        except Exception as e:
            print(f"Health check failed: {e}")
            return
            
        # 2. Create camera
        print("\n--- 2. Create Camera ---")
        resp = await client.post(f"{BASE_URL}/api/cameras", json={
            "name": "Main Gate E2E",
            "location": "Main Gate",
            "source_type": "file"
        })
        camera_id = resp.json().get("id")
        if not camera_id:
            print(f"Failed to create camera: {resp.text}")
            return
        print(f"Camera created: {camera_id}")
        
        # 3. Upload footage
        print("\n--- 3. Upload Footage ---")
        job_id = None
        with open(VIDEO_PATH, "rb") as f:
            files = {"file": ("dummy_test.mp4", f, "video/mp4")}
            data = {
                "camera_id": camera_id,
                "capture_start_utc": datetime.now(timezone.utc).isoformat()
            }
            upload_start = time.time()
            resp = await client.post(f"{BASE_URL}/api/footage", data=data, files=files)
            upload_latency = time.time() - upload_start
            print(f"Upload Latency: {upload_latency:.2f}s")
            
            if resp.status_code == 200:
                job_id = resp.json()["job_id"]
                print(f"Job created: {job_id}")
            else:
                print(f"Upload failed: {resp.text}")
                return
                
        # 4. Poll job status
        print("\n--- 4. Poll Job Status (Processing Latency) ---")
        process_start = time.time()
        while True:
            resp = await client.get(f"{BASE_URL}/api/jobs/{job_id}")
            status = resp.json().get("status")
            print(f"Status: {status}")
            if status in ["COMPLETED", "FAILED"]:
                break
            await asyncio.sleep(2)
        
        process_latency = time.time() - process_start
        print(f"Total Processing Time: {process_latency:.2f}s")
        if status != "COMPLETED":
            print("Job failed.")
            return
            
        # 5. Queries (Positive, Negative, Object, etc.)
        queries = [
            "Did a red car pass through the main gate?", # Positive/Object/Color
            "Did a person walk in the lobby?", # Negative location
            "Did anyone run yesterday?", # Temporal
            "A person in blue shirt" # Object
        ]
        
        print("\n--- 5. Evaluating Queries (Latency & Quality) ---")
        for q in queries:
            print(f"\nQuery: '{q}'")
            q_start = time.time()
            resp = await client.post(f"{BASE_URL}/api/query", json={
                "query": q,
                "clarification_answer": {"camera_id": camera_id}
            }, timeout=60.0)
            q_latency = time.time() - q_start
            if resp.status_code == 200:
                res = resp.json()
                print(f"Latency: {q_latency:.2f}s")
                print(f"Verdict: {res.get('verdict')}")
                print(f"Grounded: {res.get('grounded')}")
                print(f"Answer: {res.get('answer')}")
            else:
                print(f"Query failed: {resp.text}")
                
        total_time = time.time() - start_time
        print(f"\n--- E2E Benchmark Complete ({total_time:.2f}s) ---")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
