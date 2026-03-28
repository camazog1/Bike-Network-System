import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///dev.db")
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    PORT = int(os.environ.get("PORT", 8080))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_REPLY_TIMEOUT = int(os.environ.get("RABBITMQ_REPLY_TIMEOUT", 10))
    RABBITMQ_ENABLED = os.environ.get("RABBITMQ_ENABLED", "true").lower() == "true"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL", "sqlite:///test.db")
    RABBITMQ_ENABLED = False
