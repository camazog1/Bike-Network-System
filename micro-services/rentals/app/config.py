import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "MYSQL_URI",
        "mysql+pymysql://user:password@localhost:3306/rental_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RabbitMQ
    RABBITMQ_URL      = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "rentals")
    RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "rental.started")

    # Bike CRUD microservice
    BIKE_SERVICE_URL  = os.getenv("BIKE_SERVICE_URL", "http://localhost:8080")