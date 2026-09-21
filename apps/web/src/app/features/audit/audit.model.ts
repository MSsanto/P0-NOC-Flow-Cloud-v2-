export interface AuditEvent {
  readonly id: string;
  readonly actor_subject: string;
  readonly action: string;
  readonly resource_type: string;
  readonly resource_id: string | null;
  readonly request_id: string;
  readonly occurred_at: string;
}

export interface AuditEventPage {
  readonly items: readonly AuditEvent[];
  readonly page: number;
  readonly page_size: number;
  readonly total: number;
}
