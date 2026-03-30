from app import db
from app.models.location import BikeLocation, LocationStatus


class LocationRepository:
    def list_available(self) -> list[BikeLocation]:
        stmt = db.select(BikeLocation).where(BikeLocation.status == LocationStatus.available)
        return list(db.session.scalars(stmt))

    def get_by_bike_id(self, bike_id: str) -> BikeLocation | None:
        return db.session.get(BikeLocation, bike_id)
