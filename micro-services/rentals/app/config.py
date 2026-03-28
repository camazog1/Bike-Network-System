import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "MYSQL_URI"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RabbitMQ
    RABBITMQ_URL      = os.getenv("RABBITMQ_URL")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE")
    RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY")

    # Bike CRUD microservice
    BIKE_SERVICE_URL  = os.getenv("BIKE_SERVICE_URL")