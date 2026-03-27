from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class BrandKit(BaseModel):
    brand_name: str
    primary_color: str
    secondary_color: str
    font: str

brand_storage = {}

@router.post("/brand-kit")
async def create_brand(data: BrandKit):

    brand_storage[data.brand_name] = data

    return {
        "status": "saved",
        "brand": data
    }