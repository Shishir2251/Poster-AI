from pydantic import BaseModel
from typing import Optional

class PosterRequest(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    brand_name: Optional[str] = None
    cta_text: Optional[str] = None
    style: Optional[str] = None
    format: Optional[str] = None
    style_preset:Optional[str]= None