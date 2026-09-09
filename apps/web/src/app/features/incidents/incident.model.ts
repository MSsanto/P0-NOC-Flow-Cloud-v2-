export type IncidentSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentImpactType = 'OUTAGE' | 'DEGRADATION';
export type IncidentStatus =
  | 'OPEN'
  | 'ACKNOWLEDGED'
  | 'INVESTIGATING'
  | 'MONITORING'
  | 'RESOLVED'
  | 'CLOSED';

export interface Incident {
  readonly id: string;
  readonly title: string;
  readonly affected_resource: string;
  readonly severity: IncidentSeverity;
  readonly impact_type: IncidentImpactType;
  readonly symptoms: string;
  readonly status: IncidentStatus;
  readonly started_at: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly version: number;
}

export interface IncidentCreateRequest {
  readonly title: string;
  readonly affected_resource: string;
  readonly severity: IncidentSeverity;
  readonly impact_type: IncidentImpactType;
  readonly symptoms: string;
  readonly started_at: string;
}
