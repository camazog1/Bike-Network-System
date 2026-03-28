from flask import Blueprint, request, jsonify
from app.services.rental_service import (
    create_rental,
    BikeNotFoundException,
    BikeUnavailableException
)

rental_bp = Blueprint("rental", __name__)


@rental_bp.route("/api/v1/rental", methods=["POST"])
def create_rental_route():

    data = request.get_json(silent=True)

    # Validación: body debe ser JSON válido
    if not data:
        return jsonify({"error": "El body debe ser JSON válido."}), 400

    user_id = data.get("userId")
    bike_id = data.get("bikeId")

    # Validación: campos requeridos
    if not user_id or not bike_id:
        return jsonify({"error": "userId y bikeId son requeridos."}), 400

    # Validación: tipos correctos
    if not isinstance(user_id, str) or not isinstance(bike_id, str):
        return jsonify({"error": "userId y bikeId deben ser strings."}), 400

    # Validación: campos no vacíos
    if not user_id.strip() or not bike_id.strip():
        return jsonify({"error": "userId y bikeId no pueden estar vacíos."}), 400

    try:
        rental = create_rental(user_id=user_id, bike_id=bike_id)
        return jsonify(rental), 201

    except BikeNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    except BikeUnavailableException as e:
        return jsonify({"error": str(e)}), 409

    except Exception as e:
        return jsonify({"error": "Error interno del servidor."}), 500