import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
  SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
  SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    f"sqlite:///{BASE_DIR / 'instance' / 'health_prediction.db'}",
  )
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  # Hugging Face Inference API (optional). Get a free token at https://huggingface.co/settings/tokens
  HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "")
  HF_MODEL = os.environ.get(
    "HF_MODEL",
    "facebook/bart-large-mnli",
  )
