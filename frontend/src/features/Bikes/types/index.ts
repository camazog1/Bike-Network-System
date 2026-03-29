export interface Bike {
  id: string;
  name: string;
  brand: string;
  type: string;
  status?: string;
}

export interface BikePayload {
  name: string;
  brand: string;
  type: string;
  status?: string;
}

export type BikeData = {
  bikes: Bike[];
  page: number;
  page_size: number;
  total: number;
};
