"""RabbitMQ consumer wiring for map service.

Deployment diagram: consume ``bike.created``, ``bike.deleted``, ``rental.completed``.
Aligned with ``rentals`` publisher: direct exchange, durable queues bound by routing key.
"""

import json
import logging
from typing import Callable

import pika
from flask import Flask

logger = logging.getLogger(__name__)

ConsumerHandler = Callable[[dict], None]


def declare_binding(channel: pika.channel.Channel, exchange: str, routing_key: str) -> None:
    channel.exchange_declare(exchange=exchange, exchange_type="direct", durable=True)
    channel.queue_declare(queue=routing_key, durable=True)
    channel.queue_bind(queue=routing_key, exchange=exchange, routing_key=routing_key)


def consume_forever(
    app: Flask,
    routing_key: str,
    handler: ConsumerHandler,
) -> None:
    url = app.config["RABBITMQ_URL"]
    exchange = app.config["RABBITMQ_EXCHANGE"]

    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    declare_binding(channel, exchange, routing_key)

    def _callback(_ch, method, _properties, body):
        try:
            payload = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error("Invalid message on %s: %s", routing_key, e)
            return
        with app.app_context():
            try:
                handler(payload)
            except Exception:
                logger.exception("Handler failed for routing_key=%s", routing_key)

    channel.basic_consume(queue=routing_key, on_message_callback=_callback, auto_ack=True)
    logger.info("Consuming queue=%s exchange=%s", routing_key, exchange)
    channel.start_consuming()
