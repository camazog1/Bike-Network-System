import pika
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def publish_rental_started(rental_dict: dict):
    url      = current_app.config["RABBITMQ_URL"]
    exchange = current_app.config["RABBITMQ_EXCHANGE"]
    routing_key = current_app.config["RABBITMQ_ROUTING_KEY"]

    try:
        params     = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel    = connection.channel()

        channel.exchange_declare(
            exchange=exchange,
            exchange_type="direct",
            durable=True
        )

        channel.queue_declare(queue=routing_key, durable=True)
        channel.queue_bind(
            queue=routing_key,
            exchange=exchange,
            routing_key=routing_key
        )

        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(rental_dict),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )

        connection.close()
        logger.info(f"Evento rental.started publicado: {rental_dict['rentalId']}")

    except Exception as e:
        logger.error(f"Error publicando evento a RabbitMQ: {e}")
        raise