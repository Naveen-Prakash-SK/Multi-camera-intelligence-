from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import health, cameras, footage, memory, query
from app.core.config import settings
from app.vector.qdrant import init_qdrant

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup
    print("Initializing Multi-Camera Intelligence Backend...")
    try:
        init_qdrant()
        print("Qdrant collection initialized.")
    except Exception as e:
        print(f"Failed to initialize Qdrant: {e}")
    yield
    # Teardown
    print("Shutting down...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Core orchestration API for multi-camera intelligence",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(cameras.router)
    app.include_router(footage.router)
    app.include_router(memory.router)
    app.include_router(query.router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
