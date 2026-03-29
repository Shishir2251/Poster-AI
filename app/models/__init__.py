from pydantic import BaseModel
from typing import Optional

class LogoRequest(BaseModel):

    brand_name: str
    tagline: Optional[str] = None
    vision: Optional[str] = None
    industry: Optional[str] = None
    logo_style: Optional[str] = None
    color_palette: Optional[str] = None