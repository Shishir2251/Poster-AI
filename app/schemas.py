from pydantic import BaseModel
from typing import Optional

class PosterRequest(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    brand_name: Optional[str] = None
    cta_text: Optional[str] = None
    style: Optional[str] = "modern minimal"
    format: Optional[str] = "1:1"