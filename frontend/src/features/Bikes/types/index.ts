export interface Bike {
  id: string;
  brand: string;
  type: string;
  colour: string;
  state?: string;
}

export interface BikePayload {
  brand: string;
  type: string;
  colour: string;
  latitude: number;
  longitude: number;
  state?: string;
}

export type BikeData = {
  bikes: Bike[];
  page: number;
  page_size: number;
  total: number;
};
