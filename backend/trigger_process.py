import requests

url = "http://127.0.0.1:8000/api/process"
data = {
    "camera_id": "camera_03",
    "video_path": "data/camera_03.mp4"
}
response = requests.post(url, json=data)
print(response.json())
