import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { catchError, throwError } from 'rxjs';

import { ApiError, ProblemDetailsPayload } from './api-error';

function isProblemDetailsPayload(value: unknown): value is ProblemDetailsPayload {
  return typeof value === 'object' && value !== null;
}

function normalizeHttpError(error: HttpErrorResponse): ApiError {
  const problem = isProblemDetailsPayload(error.error) ? error.error : null;
  const requestId =
    error.headers.get('X-Request-ID') ?? problem?.request_id ?? null;
  const message =
    problem?.detail ??
    problem?.title ??
    (error.status === 0
      ? 'Não foi possível conectar à API.'
      : 'Não foi possível concluir a solicitação.');

  return new ApiError(error.status, message, requestId, problem);
}

export const apiErrorInterceptor: HttpInterceptorFn = (request, next) =>
  next(request).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse) {
        return throwError(() => normalizeHttpError(error));
      }

      return throwError(() => error);
    }),
  );
