import pytest

from app import create_app, db as _db
from app.config import TestingConfig
from app.models.location import BikeLocation, LocationStatus
from tests.mock_bike_locations import MOCK_BIKE_LOCATIONS


@pytest.fixture(scope="session")
def app():
    test_config = TestingConfig()
    test_config.SQLALCHEMY_DATABASE_URI = "sqlite://"
    _app = create_app(test_config)
    return _app


@pytest.fixture(autouse=True)
def db_session(app):
    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def seeded_mock_bike_locations(app, db_session):
    """Inserta bicis mock en la BD (vacía al inicio de cada test por db_session)."""
    for bike_id, lat, lon, status_str in MOCK_BIKE_LOCATIONS:
        db_session.add(
            BikeLocation(
                bike_id=bike_id,
                latitude=lat,
                longitude=lon,
                status=LocationStatus(status_str),
            )
        )
    db_session.commit()
