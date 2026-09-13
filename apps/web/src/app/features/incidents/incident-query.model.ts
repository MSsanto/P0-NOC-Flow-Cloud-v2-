import { Incident, IncidentSeverity, IncidentStatus } from './incident.model';

export type IncidentSortField = 'started_at' | 'updated_at';
export type SortOrder = 'asc' | 'desc';

export interface IncidentListQuery {
  readonly status?: IncidentStatus;
  readonly severity?: IncidentSeverity;
  readonly started_from?: string;
  readonly started_to?: string;
  readonly page?: number;
  readonly page_size?: number;
  readonly sort?: IncidentSortField;
  readonly order?: SortOrder;
}

export interface IncidentListResponse {
  readonly items: Incident[];
  readonly page: number;
  readonly page_size: number;
  readonly total: number;
}
