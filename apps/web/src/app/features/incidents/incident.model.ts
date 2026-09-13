export type IncidentSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type IncidentImpactType = 'OUTAGE' | 'DEGRADATION';
export type IncidentStatus =
  | 'OPEN'
  | 'ACKNOWLEDGED'
  | 'INVESTIGATING'
  | 'MONITORING'
  | 'RESOLVED'
  | 'CLOSED';
export type IncidentEventType =
  | 'INCIDENT_CREATED'
  | 'INCIDENT_UPDATED'
  | 'INCIDENT_NORMALIZED';

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

export interface IncidentEvent {
  readonly id: string;
  readonly incident_id: string;
  readonly event_type: IncidentEventType;
  readonly message: string | null;
  readonly actor_subject: string;
  readonly occurred_at: string;
}

export interface IncidentCreateRequest {
  readonly title: string;
  readonly affected_resource: string;
  readonly severity: IncidentSeverity;
  readonly impact_type: IncidentImpactType;
  readonly symptoms: string;
  readonly started_at: string;
}

export interface IncidentUpdateRequest {
  readonly message: string;
}

export interface IncidentNormalizeRequest {
  readonly note?: string;
}
