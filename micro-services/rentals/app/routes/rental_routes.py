from flask import Blueprint, request, jsonify
from app.auth.decorators import require_authentication
from app.services.rental_service import (
    create_rental,
    return_rental,
    BikeNotFoundException,
    BikeUnavailableException,
    RentalNotFoundException,
    RentalAlreadyCompletedException,
)

rental_bp = Blueprint("rental", __name__)


@rental_bp.route("/api/v1/rental", methods=["POST"])
@require_authentication
def create_rental_route():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "El body debe ser JSON válido."}), 400

    user_id = data.get("userId")
    bike_id = data.get("bikeId")

    if not user_id or not bike_id:
        return jsonify({"error": "userId y bikeId son requeridos."}), 400

    if not isinstance(user_id, str) or not isinstance(bike_id, str):
        return jsonify({"error": "userId y bikeId deben ser strings."}), 400

    if not user_id.strip() or not bike_id.strip():
        return jsonify({"error": "userId y bikeId no pueden estar vacíos."}), 400

    try:
        rental = create_rental(user_id=user_id, bike_id=bike_id)
        return jsonify(rental), 201

    except BikeNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    except BikeUnavailableException as e:
        return jsonify({"error": str(e)}), 409

    except Exception:
        return jsonify({"error": "Error interno del servidor."}), 500


@rental_bp.route("/api/v1/rental/<string:rental_id>/return", methods=["PATCH"])
@require_authentication
def return_rental_route(rental_id):

    if not rental_id or not rental_id.strip():
        return jsonify({"error": "rentalId inválido."}), 400

    try:
        rental = return_rental(rental_id=rental_id)
        return jsonify(rental), 200

    except RentalNotFoundException as e:
        return jsonify({"error": str(e)}), 404

    except RentalAlreadyCompletedException as e:
        return jsonify({"error": str(e)}), 409

    except Exception:
        return jsonify({"error": "Error interno del servidor."}), 500