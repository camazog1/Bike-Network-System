import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def get_bike(bike_id: str) -> dict:
    base_url = current_app.config["BIKE_SERVICE_URL"]
    url = f"{base_url}/api/v1/bikes/{bike_id}"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 404:
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        logger.error(f"Timeout consultando bike {bike_id}")
        raise

    except requests.exceptions.RequestException as e:
        logger.error(f"Error consultando bike {bike_id}: {e}")
        raise