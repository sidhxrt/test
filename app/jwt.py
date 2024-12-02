# JWT based authentication
# test db ka users collection has firstname and password fields

from fastapi import FastAPI, HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGOURI = os.getenv("MONGOURI)
SECRETKEY = os.getenv("SECRETKEY)

app = FastAPI()

client = MongoClient(MONGOURI) 
db = client["db"]  
users_collection = db["users"]  
tokens_collection = db["tokens"]

# JWT Configuration
SECRET_KEY = SECRETKEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

class FrontEndInput(BaseModel):
    username: str
    hashed_password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

def create_access_token(to_encode_data: dict):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode_data.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(to_encode_data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode_data.update({"exp": expire})
    refresh_token = jwt.encode(to_encode_data, SECRET_KEY, algorithm=ALGORITHM)

    # Store refresh token in MongoDB
    username = to_encode_data["sub"]
    tokens_collection.update_one(
        {"username": username},
        {"$set": {"tokenstatus.refresh_token_value": refresh_token}},
        upsert=True
    )
    return refresh_token

def verify_password(user_password: str, db_password: str) -> bool:
    if user_password == db_password:
        return True
    return False


@app.post("/token/generate")
async def generate_tokens(user_request: FrontEndInput):
    user = users_collection.find_one({"username": user_request.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user_request.hashed_password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user_request.username})
    refresh_token = create_refresh_token({"sub": user_request.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/token/refresh")
async def refresh_access_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_data = tokens_collection.find_one({"username": username})
        if user_data is None or user_data["tokenstatus"]["refresh_token_value"] != request.refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        access_token = create_access_token({"sub": username})
        return {"access_token": access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# SECURING API ENDPOINTS

from fastapi import Depends, HTTPException, Security
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token/generate") 

def verify_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token: Missing username")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/secure-endpoint")
async def secure_endpoint(username: str = Depends(verify_access_token)):
    return {"message": f"Hello, {username}"}

