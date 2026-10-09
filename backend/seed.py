import httpx
import uuid

BASE_URL = "http://localhost:8000/api"

def run_seed():
    print("Authenticating...")
    client = httpx.Client(timeout=10.0)
    r = client.post(f"{BASE_URL}/auth/login", json={"email":"admin@gmail.com", "password":"passs123456"})
    r.raise_for_status()
    token = r.json()["access_token"]
    print("Token obtained.")

    client.headers.update({"Authorization": f"Bearer {token}"})

    cameras = [
        {
            "name": "Main Gate",
            "description": "Front entrance facing street",
            "source_type": "file",
            "location": "Entrance",
            "status": "ONLINE"
        },
        {
            "name": "Lobby Cam",
            "description": "Reception area",
            "source_type": "file",
            "location": "Lobby",
            "status": "ONLINE"
        },
        {
            "name": "Loading Dock",
            "description": "Back alley loading dock",
            "source_type": "file",
            "location": "Rear",
            "status": "ONLINE"
        }
    ]

    for cam in cameras:
        r = client.post(f"{BASE_URL}/cameras", json=cam)
        if r.status_code == 200:
            print(f"Created camera: {cam['name']}")
        else:
            print(f"Failed to create {cam['name']}: {r.text}")

if __name__ == "__main__":
    run_seed()
