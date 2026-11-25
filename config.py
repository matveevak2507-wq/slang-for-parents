import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # --- MySQL (закомментировано, оставлено на будущее) ---
    # DB_HOST = os.getenv("DB_HOST", "localhost")
    # DB_PORT = int(os.getenv("DB_PORT", 3306))
    # DB_USER = os.getenv("DB_USER", "root")
    # DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    # DB_NAME = os.getenv("DB_NAME", "slang_db")
    # SQLALCHEMY_DATABASE_URI = (
    #     f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    #     "?charset=utf8mb4"
    # )

    # --- SQLite (активно) ---
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "slang.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "images", "words")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024   # 20 МБ

    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")