import os
from pathlib import Path

from dotenv import load_dotenv


# Load backend/.env regardless of the directory the server is started from
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# MySQL connection details (see backend/.env)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Websites allowed to call this API from a browser. Override with
# CORS_ORIGINS=https://mysite.com,http://localhost:5173 in backend/.env
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

# Secret used to sign login tokens. Keep it private and never change it casually:
# changing it logs everybody out.
JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    import secrets

    JWT_SECRET = secrets.token_hex(32)
    print("WARNING: JWT_SECRET missing in .env; using a temporary one (logins reset on restart)")

JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "168"))   # 7 days

# Models are tried in order. Override with GEMINI_MODELS=a,b,c in backend/.env
GEMINI_MODELS = [
    name.strip()
    for name in os.getenv(
        "GEMINI_MODELS",
        "gemini-3.8-flash,gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash"
    ).split(",")
    if name.strip()
]

print("Gemini API key loaded:", bool(GEMINI_API_KEY))