"""Background RabbitMQ consumers."""

import logging
import threading
from typing import Any

import pika
from flask import Flask

from app.messaging.rpc import send_rpc_reply

logger = logging.getLogger(__name__)


def _stub_rpc_ok(
    _app: Flask,
    _payload: dict,
    channel: pika.channel.Channel,
    method: Any,
    properties: pika.spec.BasicProperties,
) -> None:
    """Other queues still use Bike CRUD RPC — reply ok so the publisher does not timeout."""
    if properties.reply_to:
        send_rpc_reply(channel, properties, {"status": "ok"})
    channel.basic_ack(delivery_tag=method.delivery_tag)


def register_consumers(app: Flask) -> None:
    if app.config.get("TESTING"):
        return
    if not app.config.get("ENABLE_RABBIT_CONSUMERS"):
        logger.info("RabbitMQ consumers off (set ENABLE_RABBIT_CONSUMERS=1 when broker is up).")
        return

    try:
        from app.messaging.bike_created import handle_bike_created
        from app.messaging.consumer import consume_forever

        created_key = app.config["RABBITMQ_ROUTING_KEY_BIKE_CREATED"]
        deleted_key = app.config["RABBITMQ_ROUTING_KEY_BIKE_DELETED"]
        rental_key = app.config["RABBITMQ_ROUTING_KEY_RENTAL_COMPLETED"]

        def _run_bike_created() -> None:
            consume_forever(
                app,
                created_key,
                handle_bike_created,
            )

        t1 = threading.Thread(
            target=_run_bike_created,
            daemon=True,
            name=f"amqp-{created_key}",
        )
        t1.start()
        logger.info("Started consumer thread for routing_key=%s", created_key)

        for key in (deleted_key, rental_key):
            t = threading.Thread(
                target=consume_forever,
                args=(app, key, _stub_rpc_ok),
                daemon=True,
                name=f"amqp-{key}",
            )
            t.start()
            logger.info("Started consumer thread for routing_key=%s", key)
    except Exception:
        logger.exception("Could not start RabbitMQ consumers (broker up?)")
