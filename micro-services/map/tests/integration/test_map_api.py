from app import db
from app.models.location import BikeLocation, LocationStatus


class TestHealthAPI:
    def test_health_returns_ok(self, client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestAvailableLocationsAPI:
    def test_empty_database_returns_empty_array(self, client):
        response = client.get("/api/v1/locations/available")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_returns_only_available_with_bike_id_shape(self, client):
        with client.application.app_context():
            db.session.add(
                BikeLocation(
                    bike_id="BIKE-101",
                    latitude=6.2442,
                    longitude=-75.5812,
                    status=LocationStatus.available,
                )
            )
            db.session.add(
                BikeLocation(
                    bike_id="BIKE-202",
                    latitude=6.25,
                    longitude=-75.58,
                    status=LocationStatus.unavailable,
                )
            )
            db.session.commit()

        response = client.get("/api/v1/locations/available")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0] == {
            "bikeId": "BIKE-101",
            "latitude": 6.2442,
            "longitude": -75.5812,
        }
