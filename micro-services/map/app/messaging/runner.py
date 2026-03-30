"""Background RabbitMQ consumers. Handlers to be implemented in later tasks."""

import logging
import threading

from flask import Flask

logger = logging.getLogger(__name__)


def _stub_handler(payload: dict) -> None:
    logger.debug("Stub consumer received: %s", payload)


def register_consumers(app: Flask) -> None:
    if app.config.get("TESTING"):
        return
    if not app.config.get("ENABLE_RABBIT_CONSUMERS"):
        logger.info("RabbitMQ consumers off (set ENABLE_RABBIT_CONSUMERS=1 when broker is up).")
        return

    # TODO: replace stubs with bike.created / bike.deleted / rental.completed handlers
    try:
        from app.messaging.consumer import consume_forever

        keys = [
            app.config["RABBITMQ_ROUTING_KEY_BIKE_CREATED"],
            app.config["RABBITMQ_ROUTING_KEY_BIKE_DELETED"],
            app.config["RABBITMQ_ROUTING_KEY_RENTAL_COMPLETED"],
        ]
        for key in keys:
            t = threading.Thread(
                target=consume_forever,
                args=(app, key, _stub_handler),
                daemon=True,
                name=f"amqp-{key}",
            )
            t.start()
            logger.info("Started consumer thread for routing_key=%s", key)
    except Exception:
        logger.exception("Could not start RabbitMQ consumers (broker up?)")
