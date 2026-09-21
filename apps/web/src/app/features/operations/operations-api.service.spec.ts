import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { environment } from '../../../environments/environment';
import { OperationsApiService } from './operations-api.service';

describe('OperationsApiService', () => {
  let service: OperationsApiService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(OperationsApiService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('loads dashboard summary', () => {
    service.dashboard().subscribe();
    http.expectOne(`${environment.apiBaseUrl}/dashboard/summary`).flush({
      active_count: 0,
      critical_active_count: 0,
      resolved_in_shift_count: 0,
      shift: { window_start: '2026-09-21T06:00:00Z', window_end: '2026-09-21T18:00:00Z' },
      items: [],
    });
  });

  it('finalizes handover without client authority fields', () => {
    service.finalize('Turno acompanhado.').subscribe();
    const request = http.expectOne(`${environment.apiBaseUrl}/handovers`);
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ observations: 'Turno acompanhado.' });
    request.flush({
      id: '00000000-0000-4000-8000-000000000001',
      version: 1,
      window_start: '2026-09-21T06:00:00Z',
      window_end: '2026-09-21T18:00:00Z',
      observations: 'Turno acompanhado.',
      finalized_by_subject: 'demo',
      finalized_at: '2026-09-21T17:00:00Z',
      items: [],
    });
  });

  it('loads paginated handover history', () => {
    service.history(2, 10).subscribe();
    const request = http.expectOne(
      (req) => req.url === `${environment.apiBaseUrl}/handovers`
        && req.params.get('page') === '2'
        && req.params.get('page_size') === '10',
    );
    expect(request.request.method).toBe('GET');
    request.flush({ items: [], page: 2, page_size: 10, total: 0 });
  });
});
