from pathlib import Path

from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE_BY_CONFIG = {
    "development": ".env.dev",
    "testing": ".env.test",
    "production": ".env.prod",
}

flask_config = os.getenv("FLASK_CONFIG", "development")
load_dotenv(BASE_DIR / ENV_FILE_BY_CONFIG.get(flask_config, ".env.dev"))
load_dotenv(BASE_DIR / ".env")


def _secret_key():
    secret_key = os.getenv("SECRET_KEY")
    if secret_key:
        return secret_key
    if flask_config == "production":
        raise RuntimeError("SECRET_KEY precisa estar configurada em producao")
    return "dev-secret-key"


class Config:
    SECRET_KEY = _secret_key()
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///unihub.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config():
    env_name = os.getenv("FLASK_CONFIG", "development")
    return config_by_name.get(env_name, DevelopmentConfig)
