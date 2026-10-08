import httpx
import asyncio

async def add_camera():
    url = "http://localhost:8000/api/cameras"
    payload = {
        "name": "Live API Camera",
        "description": "Live Stream from Dev Tunnel",
        "source_type": "live",
        "stream_url": "https://3h2t93jj-8001.inc1.devtunnels.ms/",
        "location": "Live Camera 1"
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(add_camera())
