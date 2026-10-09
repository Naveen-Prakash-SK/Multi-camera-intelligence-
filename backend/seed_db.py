import asyncio
import uuid
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import AsyncSessionLocal
from app.models.core import Camera

async def seed_db():
    async with AsyncSessionLocal() as session:
        cameras = [
            Camera(
                id=str(uuid.uuid4()),
                name="Main Gate",
                description="Front entrance facing street",
                source_type="file",
                location="Entrance",
                status="ONLINE",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            Camera(
                id=str(uuid.uuid4()),
                name="Lobby Cam",
                description="Reception area",
                source_type="file",
                location="Lobby",
                status="ONLINE",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            ),
            Camera(
                id=str(uuid.uuid4()),
                name="Loading Dock",
                description="Back alley loading dock",
                source_type="file",
                location="Rear",
                status="ONLINE",
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow()
            )
        ]
        session.add_all(cameras)
        await session.commit()
        print("Successfully seeded database directly.")

if __name__ == "__main__":
    asyncio.run(seed_db())
