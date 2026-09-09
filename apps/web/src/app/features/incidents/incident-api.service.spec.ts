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

  it('lists incidents from the versioned API', () => {
    service.list().subscribe();
    const request = controller.expectOne('/api/v1/incidents');
    expect(request.request.method).toBe('GET');
    request.flush([]);
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
    const request = controller.expectOne('/api/v1/incidents');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual(payload);
    expect(request.request.body.tenant_id).toBeUndefined();
    request.flush({});
  });

  it('loads detail using the incident id', () => {
    service.get('abc-123').subscribe();
    const request = controller.expectOne('/api/v1/incidents/abc-123');
    expect(request.request.method).toBe('GET');
    request.flush({});
  });
});
