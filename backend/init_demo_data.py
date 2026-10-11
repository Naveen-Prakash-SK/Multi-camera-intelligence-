import requests

base_url = "http://localhost:8000/api"

cameras = [
    {"camera_id": "camera_01", "camera_name": "Main Gate", "location": "Entrance"},
    {"camera_id": "camera_02", "camera_name": "Lobby", "location": "First Floor"},
    {"camera_id": "camera_03", "camera_name": "Parking", "location": "Basement"}
]

for cam in cameras:
    res = requests.post(f"{base_url}/cameras", json=cam)
    print(f"Registered {cam['camera_name']}: {res.status_code}")

print("Done registering cameras.")
