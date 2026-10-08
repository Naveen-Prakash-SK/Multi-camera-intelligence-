import httpx
import asyncio

async def add_camera():
    url = "http://localhost:8000/api/cameras"
    payload = {
        "name": "Live API Camera",
        "description": "Live Stream from Dev Tunnel",
        "source_type": "live",
        "stream_url": "http://127.0.0.1:8001/api/stream/CAM01",
        "location": "Live Camera 1"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(add_camera())
