import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { IncidentApiService } from './incident-api.service';
import { IncidentCreateRequest } from './incident.model';

describe('IncidentApiService', () => {
  let service: IncidentApiService;
  let controller: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(IncidentApiService);
    controller = TestBed.inject(HttpTestingController);
  });

  afterEach(() => controller.verify());

  it('lists incidents with validated query parameters', () => {
    service
      .list({
        status: 'OPEN',
        severity: 'HIGH',
        page: 2,
        page_size: 25,
        sort: 'updated_at',
        order: 'asc',
      })
      .subscribe();

    const request = controller.expectOne((candidate) =>
      candidate.url.endsWith('/api/v1/incidents/query'),
    );
    expect(request.request.method).toBe('GET');
    expect(request.request.params.get('status')).toBe('OPEN');
    expect(request.request.params.get('severity')).toBe('HIGH');
    expect(request.request.params.get('page')).toBe('2');
    expect(request.request.params.get('page_size')).toBe('25');
    expect(request.request.params.get('sort')).toBe('updated_at');
    expect(request.request.params.get('order')).toBe('asc');
    request.flush({ items: [], page: 2, page_size: 25, total: 0 });
  });

  it('creates an incident without authority fields', () => {
    const payload: IncidentCreateRequest = {
      title: 'WAN indisponível',
      affected_resource: 'WAN Loja 001',
      severity: 'HIGH',
      impact_type: 'OUTAGE',
      symptoms: 'Conectividade indisponível para a unidade.',
      started_at: '2026-09-09T12:00:00.000Z',
    };

    service.create(payload).subscribe();
    const request = controller.expectOne((candidate) => candidate.url.endsWith('/api/v1/incidents'));
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    expect(request.request.body.tenant_id).toBeUndefined();
    request.flush({});
  });

  it('loads detail using the incident id', () => {
    service.get('abc-123').subscribe();
    const request = controller.expectOne((candidate) => candidate.url.endsWith('/api/v1/incidents/abc-123'));
    expect(request.request.method).toBe('GET');
    request.flush({});
  });

  it('loads the incident timeline', () => {
    service.timeline('abc-123').subscribe();
    const request = controller.expectOne((candidate) =>
      candidate.url.endsWith('/api/v1/incidents/abc-123/timeline'),
    );
    expect(request.request.method).toBe('GET');
    request.flush([]);
  });

  it('posts an operational update without authority fields', () => {
    service.addUpdate('abc-123', { message: 'Operadora acionada.' }).subscribe();
    const request = controller.expectOne((candidate) =>
      candidate.url.endsWith('/api/v1/incidents/abc-123/updates'),
    );
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ message: 'Operadora acionada.' });
    expect(request.request.body.actor_subject).toBeUndefined();
    expect(request.request.body.tenant_id).toBeUndefined();
    request.flush({});
  });

  it('posts normalization with an optional note', () => {
    service.normalize('abc-123', { note: 'Serviço restabelecido.' }).subscribe();
    const request = controller.expectOne((candidate) =>
      candidate.url.endsWith('/api/v1/incidents/abc-123/normalize'),
    );
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ note: 'Serviço restabelecido.' });
    expect(request.request.body.actor_subject).toBeUndefined();
    request.flush({});
  });
});
