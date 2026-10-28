import os
import urllib.parse
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Explicitly load .env from project root directory
load_dotenv(os.path.join(BASE_DIR, ".env"))


def build_database_uri() -> str:
    """Build MySQL database URI compatible with XAMPP or standalone MySQL Server."""
    explicit_uri = os.getenv("DATABASE_URL")
    if explicit_uri:
        # Standardize mysql:// to mysql+pymysql://
        if explicit_uri.startswith("mysql://"):
            explicit_uri = "mysql+pymysql://" + explicit_uri[len("mysql://"):]
        return explicit_uri

    # Read component parameters with robust fallback
    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "root")
    # For XAMPP, password is empty by default; for local MySQL 8.0, Abc@1234
    password = os.getenv("MYSQL_PASSWORD", "Abc@1234")
    db_name = os.getenv("MYSQL_DB", "skillverify")

    encoded_pw = urllib.parse.quote_plus(password) if password else ""
    return f"mysql+pymysql://{user}:{encoded_pw}@{host}:{port}/{db_name}?charset=utf8mb4"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "skillverify-secure-dev-session-key-2026")
    
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    CERTIFICATE_FOLDER = os.path.join(BASE_DIR, "uploads", "certificates")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB resume limit

    # Phase 1: Certificate Eligibility Threshold (Percentage: 60.0%)
    CERTIFICATE_THRESHOLD = float(os.getenv("CERTIFICATE_THRESHOLD", "60.0"))

    # Google Gemini API Key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SERVER_NAME = "localhost"
