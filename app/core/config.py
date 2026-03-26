import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings:

    def __init__(self):
        # API Settings
        self.PROJECT_NAME = "Poster Generation API"
        self.API_VERSION = "1.0"

        # OpenAI
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.9"))

        # File Storage
        self.UPLOAD_DIR = BASE_DIR / "uploads"
        self.GENERATED_DIR = BASE_DIR / "generated"
        self.FONT_DIR = BASE_DIR / "fonts"

        # System Limits
        self.MAX_REGENERATIONS = 3
        self.MAX_IMAGE_SIZE_MB = 10
        self.ALLOWED_IMAGE_TYPES = ["image/png", "image/jpeg", "image/jpg"]

        # Performance
        self.MAX_CONCURRENT_USERS_PER_MIN = 100
        self.MAX_USERS_PER_DAY = 1000

        # Poster Defaults
        self.DEFAULT_HEADLINE_FONT = "Inter-Bold.ttf"
        self.DEFAULT_BODY_FONT = "Inter-Regular.ttf"
        self.DEFAULT_POSTER_WIDTH = 1080
        self.DEFAULT_POSTER_HEIGHT = 1080

        # Language
        self.DEFAULT_LANGUAGE = "en"
        self.HEBREW_LANGUAGE_CODE = "he"


settings = Settings()

# Ensure folders exist
settings.UPLOAD_DIR.mkdir(exist_ok=True)
settings.GENERATED_DIR.mkdir(exist_ok=True)