import { Marker, Popup } from "react-leaflet";
import type { BikeMarkerProps } from "../types";

export default function BikeMarker({ bike }: BikeMarkerProps) {
  return (
    <Marker position={[bike.latitude, bike.longitude]}>
      <Popup>
        <div>
          <p className="font-semibold">Bike</p>
          <p className="font-semibold text-small">ID: {bike.bikeId}</p>
          <div className="flex gap-2 justify-between items-center">
            <p className="text-sm text-green-600">Available</p>
            <button className="px-3 py-1 bg-brand-500 text-white rounded hover:bg-brand-600 max-h-8">
              Rent
            </button>
          </div>
        </div>
      </Popup>
    </Marker>
  );
}
