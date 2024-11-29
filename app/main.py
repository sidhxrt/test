from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.api import root
from dotenv import load_dotenv
import os

# API Key Configuration
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# API key validation function
async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=403,
            detail="Could not validate API key",
        )

app = FastAPI()

# Include the router with API key dependency applied globally
app.include_router(root.router, dependencies=[Depends(get_api_key)])
