"""
from fastapi import APIRouter
from dotenv import load_dotenv
from pydantic import BaseModel
from app.utils.helper import helper, hashingfunction

load_dotenv()   
 
router = APIRouter()
    
class SampleRequest(BaseModel):
    id: int

@router.get("/try")
async def read_root():
    msg = helper()
    return msg

@router.post("/try")
async def create_note(user_input: SampleRequest):
    hashedid = hashingfunction(user_input.id)
    return hashedid
"""