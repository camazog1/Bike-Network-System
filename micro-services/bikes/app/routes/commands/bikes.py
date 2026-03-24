from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.repositories.bike_repository import BikeRepository
from app.schemas.bike import BikeCreate, BikeUpdate
from app.services.bike_service import BikeService

commands_bp = Blueprint("commands_bikes", __name__)


def _get_service() -> BikeService:
    return BikeService(BikeRepository())


@commands_bp.route("/api/v1/bikes", methods=["POST"])
def create_bike():
    try:
        data = BikeCreate.model_validate(request.get_json())
    except ValidationError as e:
        errors = e.errors()
        first = errors[0] if errors else {}
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": f"Invalid value for field '{first.get('loc', ['unknown'])[0]}'.",
            "details": {"errors": [{
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", ""),
            } for err in errors]},
        }), 422

    service = _get_service()
    response = service.create_bike(data)
    return jsonify(response.model_dump(mode="json")), 201


@commands_bp.route("/api/v1/bikes/<string:id>", methods=["PUT"])
def update_bike(id):
    try:
        data = BikeUpdate.model_validate(request.get_json())
    except ValidationError as e:
        errors = e.errors()
        first = errors[0] if errors else {}
        return jsonify({
            "code": "VALIDATION_ERROR",
            "message": f"Invalid value for field '{first.get('loc', ['unknown'])[0]}'.",
            "details": {"errors": [{
                "field": ".".join(str(loc) for loc in err.get("loc", [])),
                "message": err.get("msg", ""),
            } for err in errors]},
        }), 422

    service = _get_service()
    response = service.update_bike(id, data)
    return jsonify(response.model_dump(mode="json")), 200


@commands_bp.route("/api/v1/bikes/<string:id>", methods=["DELETE"])
def delete_bike(id):
    service = _get_service()
    service.delete_bike(id)
    return "", 204
