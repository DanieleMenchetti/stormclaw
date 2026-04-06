"""
Configuration - loaded from environment variables or .env file
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    ALLOWED_CHAT_IDS: list[int] = None

    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_PATH: str = os.getenv("LOG_PATH", "./logs")

    def __post_init__(self):
        raw_ids = os.getenv("ALLOWED_CHAT_IDS", "")
        if raw_ids:
            self.ALLOWED_CHAT_IDS = [int(i.strip()) for i in raw_ids.split(",")]
        else:
            self.ALLOWED_CHAT_IDS = []  # empty = allow all

    def validate(self):
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")


config = Config()