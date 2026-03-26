import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings:

    # API Settings
    PROJECT_NAME: str = "Poster Generation API"
    API_VERSION: str = "1.0"

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    OPENAI_MODEL: str = os.getenv(
        "OPENAI_MODEL",
        "gpt-4o-mini"
    )

    OPENAI_TEMPERATURE: float = float(
        os.getenv("OPENAI_TEMPERATURE", 0.9)
    )

    # File Storage
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    GENERATED_DIR: Path = BASE_DIR / "generated"
    FONT_DIR: Path = BASE_DIR / "fonts"

    # System Limits
    MAX_REGENERATIONS: int = 3

    MAX_IMAGE_SIZE_MB: int = 10

    ALLOWED_IMAGE_TYPES = [
        "image/png",
        "image/jpeg",
        "image/jpg"
    ]

    # Performance
    MAX_CONCURRENT_USERS_PER_MIN: int = 100
    MAX_USERS_PER_DAY: int = 1000

    # Poster Defaults
    DEFAULT_HEADLINE_FONT = "Inter-Bold.ttf"
    DEFAULT_BODY_FONT = "Inter-Regular.ttf"

    DEFAULT_POSTER_WIDTH = 1080
    DEFAULT_POSTER_HEIGHT = 1080

    # Language
    DEFAULT_LANGUAGE = "en"
    HEBREW_LANGUAGE_CODE = "he"


settings = Settings()

# Ensure folders exist
settings.UPLOAD_DIR.mkdir(exist_ok=True)
settings.GENERATED_DIR.mkdir(exist_ok=True)