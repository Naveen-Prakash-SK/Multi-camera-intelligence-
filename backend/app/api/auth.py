from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone
import os

router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key-for-24hr-ku")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/api/auth/login", response_model=Token)
async def login(req: LoginRequest):
    if req.email == "admin@gmail.com" and req.password == "passs123456":
        access_token = create_access_token(data={"sub": req.email})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
