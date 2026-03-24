import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    PORT = int(os.environ.get("PORT", 8080))
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL", "sqlite:///test.db")
