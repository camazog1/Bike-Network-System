import pika
import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)


def _publish(routing_key: str, payload: dict):
    url         = current_app.config["RABBITMQ_URL"]
    exchange    = current_app.config["RABBITMQ_EXCHANGE"]

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
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json"
        )
    )

    connection.close()
    logger.info(f"Evento '{routing_key}' publicado: {payload}")


def publish_rental_started(rental_dict: dict):
    try:
        routing_key = current_app.config["RABBITMQ_ROUTING_KEY"]
        _publish(routing_key, rental_dict)
    except Exception as e:
        logger.error(f"Error publicando rental.started: {e}")
        raise


def publish_rental_ended(rental_dict: dict):
    try:
        _publish("rental.ended", {
            "rentalId": rental_dict["rentalId"],
            "bikeId":   rental_dict["bikeId"],
            "userId":   rental_dict["userId"],
            "endTime":  rental_dict["endTime"],
        })
    except Exception as e:
        logger.error(f"Error publicando rental.ended: {e}")
        raise