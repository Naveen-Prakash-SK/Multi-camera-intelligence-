import requests
import time
import subprocess
import uuid
import os

API_URL = "http://localhost:8000/api"

def test_clarify_once():
    print("Running Clarify-Once Restart Test...")
    
    # Ensure a camera exists to map to
    cam_id = str(uuid.uuid4())
    requests.post(f"{API_URL}/cameras", json={"id": cam_id, "name": "Camera 03", "location": "Main Gate"})
    
    query = "Did a person enter the Main Gate?"
    
    # 1. First query should request clarification
    print("1. First query (expecting clarification)...")
    res1 = requests.post(f"{API_URL}/query", json={"query": query})
    data1 = res1.json()
    assert data1["verdict"] == "CLARIFICATION_REQUIRED", f"Expected CLARIFICATION_REQUIRED, got {data1['verdict']}"
    print("  -> Clarification requested successfully.")
    
    # 2. Provide clarification
    print("2. Providing clarification (Main Gate -> Camera 03)...")
    res2 = requests.post(f"{API_URL}/query", json={
        "query": query, 
        "clarification_answer": {"camera_id": cam_id}
    })
    data2 = res2.json()
    assert data2["verdict"] != "CLARIFICATION_REQUIRED", "Should not request clarification again."
    print("  -> Mapping saved successfully.")
    
    # 3. Restart Docker Services
    print("3. Restarting backend to test persistence...")
    subprocess.run(["docker", "compose", "restart", "backend"], check=True)
    time.sleep(10) # Wait for backend to come up
    
    # 4. Query again after restart
    print("4. Executing same query after restart...")
    res3 = requests.post(f"{API_URL}/query", json={"query": query})
    data3 = res3.json()
    
    assert data3["verdict"] != "CLARIFICATION_REQUIRED", "Failed: System forgot the scene memory mapping after restart."
    print("  -> Success! System remembered the mapping after restart.")
    print("Test passed successfully.")

if __name__ == "__main__":
    try:
        test_clarify_once()
    except Exception as e:
        print(f"Test Failed: {e}")
