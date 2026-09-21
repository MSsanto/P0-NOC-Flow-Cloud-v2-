import { IncidentSeverity, IncidentStatus } from '../incidents/incident.model';

export interface ShiftWindow {
  readonly window_start: string;
  readonly window_end: string;
}

export interface DashboardItem {
  readonly id: string;
  readonly title: string;
  readonly affected_resource: string;
  readonly severity: IncidentSeverity;
  readonly status: IncidentStatus;
  readonly started_at: string;
  readonly updated_at: string;
}

export interface DashboardSummary {
  readonly active_count: number;
  readonly critical_active_count: number;
  readonly resolved_in_shift_count: number;
  readonly shift: ShiftWindow;
  readonly items: readonly DashboardItem[];
}

export interface HandoverItem {
  readonly incident_id: string;
  readonly title: string;
  readonly affected_resource: string;
  readonly severity: IncidentSeverity;
  readonly status: IncidentStatus;
  readonly started_at: string;
  readonly last_event_message: string | null;
  readonly last_event_at: string | null;
}

export interface HandoverPreview {
  readonly window_start: string;
  readonly window_end: string;
  readonly generated_at: string;
  readonly items: readonly HandoverItem[];
}

export interface Handover {
  readonly id: string;
  readonly version: number;
  readonly window_start: string;
  readonly window_end: string;
  readonly observations: string | null;
  readonly finalized_by_subject: string;
  readonly finalized_at: string;
  readonly items: readonly HandoverItem[];
}

export interface HandoverHistoryItem {
  readonly id: string;
  readonly version: number;
  readonly window_start: string;
  readonly window_end: string;
  readonly finalized_by_subject: string;
  readonly finalized_at: string;
}

export interface HandoverHistory {
  readonly items: readonly HandoverHistoryItem[];
  readonly page: number;
  readonly page_size: number;
  readonly total: number;
}
