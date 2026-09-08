import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { firstValueFrom } from 'rxjs';

import { ApiError } from './api-error';
import { apiErrorInterceptor } from './api-error.interceptor';
import { HttpClient } from '@angular/common/http';

describe('apiErrorInterceptor', () => {
  let http: HttpClient;
  let controller: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([apiErrorInterceptor])),
        provideHttpClientTesting(),
      ],
    });

    http = TestBed.inject(HttpClient);
    controller = TestBed.inject(HttpTestingController);
  });

  afterEach(() => controller.verify());

  it('normalizes Problem Details and preserves request ID', async () => {
    const response = firstValueFrom(http.get('/api/v1/incidents'));
    const request = controller.expectOne('/api/v1/incidents');

    request.flush(
      {
        title: 'Recurso não encontrado',
        detail: 'Incidente não encontrado.',
        status: 404,
      },
      {
        status: 404,
        statusText: 'Not Found',
        headers: { 'X-Request-ID': 'req-123' },
      },
    );

    await expect(response).rejects.toMatchObject<ApiError>({
      name: 'ApiError',
      status: 404,
      message: 'Incidente não encontrado.',
      requestId: 'req-123',
    });
  });
});
