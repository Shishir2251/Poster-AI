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


def get_language_rules(language: str):
    rtl_languages = ["hebrew", "arabic", "urdu"]

    rules = f"""
LANGUAGE RULE:
- All visible text MUST be in {language}
- Do NOT use English unless explicitly requested
- Ensure fluent, natural, native-level {language}
"""

    if language in rtl_languages:
        rules += """
TEXT DIRECTION RULE:
- Use right-to-left (RTL) layout
- Align text accordingly
- Ensure proper grammar and punctuation
"""

    return rules