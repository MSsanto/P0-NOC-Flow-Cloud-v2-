export interface ProblemDetailsPayload {
  readonly type?: string;
  readonly title?: string;
  readonly status?: number;
  readonly detail?: string;
  readonly instance?: string;
  readonly request_id?: string;
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly requestId: string | null = null,
    public readonly problem: ProblemDetailsPayload | null = null,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
