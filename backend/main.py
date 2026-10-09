from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.api import health, cameras, footage, memory, query, evidence, timeline, standing_queries, auth
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

    import jwt
    import os
    from fastapi import Request
    from fastapi.responses import JSONResponse
    
    @app.middleware("http")
    async def verify_jwt_token(request: Request, call_next):
        # Exclude open routes
        open_routes = ["/api/auth/login", "/api/health", "/docs", "/openapi.json"]
        if request.url.path in open_routes or request.method == "OPTIONS" or request.url.path.startswith("/app/storage"):
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        elif request.query_params.get("token"):
            token = request.query_params.get("token")
            
        if not token:
            return JSONResponse(
                status_code=401, 
                content={"detail": "Missing or invalid token"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
        try:
            # We use the same secret and algorithm as in auth.py
            jwt.decode(token, os.getenv("JWT_SECRET", "super-secret-key-for-24hr-ku"), algorithms=["HS256"])
        except Exception as e:
            print(f"JWT Verification Failed: {e}")
            return JSONResponse(
                status_code=401, 
                content={"detail": "Invalid or expired token"},
                headers={"Access-Control-Allow-Origin": "*"}
            )
            
        return await call_next(request)


    # Serve static files from storage
    import os
    os.makedirs("/app/storage", exist_ok=True)
    app.mount("/app/storage", StaticFiles(directory="/app/storage"), name="storage")

    # Include routers
    app.include_router(auth.router)
    app.include_router(health.router)
    app.include_router(cameras.router)
    app.include_router(footage.router)
    app.include_router(memory.router)
    app.include_router(query.router)
    app.include_router(evidence.router)
    app.include_router(timeline.router)
    app.include_router(standing_queries.router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
