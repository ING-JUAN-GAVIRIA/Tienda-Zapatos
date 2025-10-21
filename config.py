import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esto-por-una-clave-secreta-larga")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:juandiego@localhost:5432/tienda_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None
