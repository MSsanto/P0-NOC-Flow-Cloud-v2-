import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { AppPermission, AuthContextService } from '../../core/auth/auth-context.service';
import { IncidentApiService } from './incident-api.service';
import { IncidentDetailPageComponent } from './incident-detail-page.component';
import {
  Incident,
  IncidentEvent,
  IncidentNormalizeRequest,
  IncidentUpdateRequest,
} from './incident.model';

const baseIncident: Incident = {
  id: 'inc-1',
  title: 'WAN indisponível',
  affected_resource: 'WAN Loja 001',
  severity: 'HIGH',
  impact_type: 'OUTAGE',
  symptoms: 'Conectividade indisponível para a unidade.',
  status: 'OPEN',
  started_at: '2026-09-13T12:00:00.000Z',
  created_at: '2026-09-13T12:20:00.000Z',
  updated_at: '2026-09-13T12:20:00.000Z',
  version: 1,
};

const createdEvent: IncidentEvent = {
  id: 'event-1',
  incident_id: 'inc-1',
  event_type: 'INCIDENT_CREATED',
  message: null,
  actor_subject: 'demo-operator',
  occurred_at: '2026-09-13T12:20:00.000Z',
};

class IncidentApiStub {
  lastUpdate: IncidentUpdateRequest | null = null;
  lastNormalize: IncidentNormalizeRequest | null = null;

  get() {
    return of(baseIncident);
  }

  timeline() {
    return of([createdEvent]);
  }

  addUpdate(_id: string, payload: IncidentUpdateRequest) {
    this.lastUpdate = payload;
    return of({ ...baseIncident, version: 2, updated_at: '2026-09-13T12:30:00.000Z' });
  }

  normalize(_id: string, payload: IncidentNormalizeRequest) {
    this.lastNormalize = payload;
    return of({
      ...baseIncident,
      status: 'RESOLVED' as const,
      version: 2,
      updated_at: '2026-09-13T12:40:00.000Z',
    });
  }
}

class AuthContextStub {
  writable = true;

  can(permission: AppPermission): boolean {
    return permission === 'incident:read' || this.writable;
  }
}

describe('IncidentDetailPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IncidentDetailPageComponent],
      providers: [
        provideRouter([]),
        { provide: IncidentApiService, useClass: IncidentApiStub },
        { provide: AuthContextService, useClass: AuthContextStub },
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: convertToParamMap({ id: 'inc-1' }) } },
        },
      ],
    }).compileComponents();
  });

  it('renders operational actions and the append-only timeline', () => {
    const fixture = TestBed.createComponent(IncidentDetailPageComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('Ações do incidente');
    expect(element.textContent).toContain('Adicionar atualização');
    expect(element.textContent).toContain('Normalizar incidente');
    expect(element.textContent).toContain('Timeline');
    expect(element.textContent).toContain('Incidente criado');
    expect(element.textContent).toContain('demo-operator');
  });

  it('trims and submits an operational update', () => {
    const fixture = TestBed.createComponent(IncidentDetailPageComponent);
    const component = fixture.componentInstance;
    const api = TestBed.inject(IncidentApiService) as unknown as IncidentApiStub;
    fixture.detectChanges();

    component.updateMessage.setValue('  Operadora acionada.  ');
    component.submitUpdate(new Event('submit'));
    fixture.detectChanges();

    expect(api.lastUpdate).toEqual({ message: 'Operadora acionada.' });
    expect(component.incident()?.version).toBe(2);
    expect(component.actionSuccess()).toContain('registrada');
  });

  it('requires explicit confirmation before normalization and disables actions after resolution', () => {
    const fixture = TestBed.createComponent(IncidentDetailPageComponent);
    const component = fixture.componentInstance;
    const api = TestBed.inject(IncidentApiService) as unknown as IncidentApiStub;
    fixture.detectChanges();

    component.openNormalize();
    expect(component.showNormalize()).toBe(true);
    expect(api.lastNormalize).toBeNull();

    component.normalizeNote.setValue('  Serviço restabelecido.  ');
    component.confirmNormalize();
    fixture.detectChanges();

    expect(api.lastNormalize).toEqual({ note: 'Serviço restabelecido.' });
    expect(component.incident()?.status).toBe('RESOLVED');
    expect(component.isActive()).toBe(false);
    expect(component.showNormalize()).toBe(false);
  });

  it('keeps a viewer read-only while preserving timeline visibility', () => {
    const auth = TestBed.inject(AuthContextService) as unknown as AuthContextStub;
    auth.writable = false;

    const fixture = TestBed.createComponent(IncidentDetailPageComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).toContain('acesso somente de leitura');
    expect(element.textContent).not.toContain('Adicionar atualização');
    expect(element.textContent).not.toContain('Normalizar incidente');
    expect(element.textContent).toContain('Timeline');
  });
});
