import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY'), "dev-secret-change-in-production"
    SQLALCHEMY_DATABASE_URI = "sqlite:///auth.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-secret-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)