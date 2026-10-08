from fastapi import FastAPI
from app.api import health, cameras, footage, memory, query
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Core orchestration API for multi-camera intelligence"
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
