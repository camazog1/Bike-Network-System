import logging
from app import db
from app.models.rental import Rental
from app.services.bike_service import get_bike
from app.messaging.publisher import publish_rental_started

logger = logging.getLogger(__name__)

def create_rental(user_id: str, bike_id: str) -> dict:
    # 1. Verificar que la bici existe
    bike = get_bike(bike_id)
    if bike is None:
        raise BikeNotFoundException(f"Bici {bike_id} no encontrada.")

    # 2. Verificar que la bici está disponible
    if bike.get("state", "").lower() != "free":
        raise BikeUnavailableException(f"Bici {bike_id} no está disponible.")

    # 3. Crear el registro de renta en MySQL
    rental = Rental(user_id=user_id, bike_id=bike_id)
    db.session.add(rental)
    db.session.commit()
    logger.info(f"Rental creado: {rental.rental_id}")

    # 4. Publicar evento rental.started a RabbitMQ
    try:
        publish_rental_started(rental.to_dict())
    except Exception as e:
        # Si falla RabbitMQ se hace rollback
        db.session.delete(rental)
        db.session.commit()
        logger.error(f"Rollback rental {rental.rental_id} por fallo en RabbitMQ: {e}")
        raise

    return rental.to_dict()

# Excepciones propias del dominio
class BikeNotFoundException(Exception):
    pass

class BikeUnavailableException(Exception):
    pass