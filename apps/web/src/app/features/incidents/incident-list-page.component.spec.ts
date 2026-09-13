import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of } from 'rxjs';

import { IncidentApiService } from './incident-api.service';
import { IncidentListQuery } from './incident-query.model';
import { IncidentListPageComponent } from './incident-list-page.component';
import { Incident } from './incident.model';

const incident: Incident = {
  id: 'inc-1',
  title: 'WAN indisponível',
  affected_resource: 'WAN Loja 001',
  severity: 'HIGH',
  impact_type: 'OUTAGE',
  symptoms: 'Conectividade indisponível para a unidade.',
  status: 'OPEN',
  started_at: '2026-09-13T12:00:00.000Z',
  created_at: '2026-09-13T12:05:00.000Z',
  updated_at: '2026-09-13T12:05:00.000Z',
  version: 1,
};

class IncidentApiStub {
  readonly queries: IncidentListQuery[] = [];

  list(query: IncidentListQuery) {
    this.queries.push(query);
    return of({
      items: [incident],
      page: query.page ?? 1,
      page_size: query.page_size ?? 25,
      total: 30,
    });
  }
}

describe('IncidentListPageComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IncidentListPageComponent],
      providers: [
        provideRouter([]),
        { provide: IncidentApiService, useClass: IncidentApiStub },
      ],
    }).compileComponents();
  });

  it('loads the first page with the default ordering', () => {
    const fixture = TestBed.createComponent(IncidentListPageComponent);
    const api = TestBed.inject(IncidentApiService) as unknown as IncidentApiStub;
    fixture.detectChanges();

    expect(api.queries[0]).toEqual({
      page: 1,
      page_size: 25,
      sort: 'started_at',
      order: 'desc',
    });
    expect(fixture.componentInstance.total()).toBe(30);
    expect(fixture.componentInstance.hasNext()).toBe(true);
  });

  it('applies status, severity and sorting filters', () => {
    const fixture = TestBed.createComponent(IncidentListPageComponent);
    const component = fixture.componentInstance;
    const api = TestBed.inject(IncidentApiService) as unknown as IncidentApiStub;
    fixture.detectChanges();

    component.statusFilter.setValue('OPEN');
    component.severityFilter.setValue('HIGH');
    component.sortOption.setValue('updated_at:asc');
    component.applyFilters(new Event('submit'));

    expect(api.queries.at(-1)).toMatchObject({
      status: 'OPEN',
      severity: 'HIGH',
      page: 1,
      page_size: 25,
      sort: 'updated_at',
      order: 'asc',
    });
  });

  it('requests the next page while preserving the active query', () => {
    const fixture = TestBed.createComponent(IncidentListPageComponent);
    const component = fixture.componentInstance;
    const api = TestBed.inject(IncidentApiService) as unknown as IncidentApiStub;
    fixture.detectChanges();

    component.severityFilter.setValue('HIGH');
    component.applyFilters(new Event('submit'));
    component.nextPage();

    expect(api.queries.at(-1)).toMatchObject({ severity: 'HIGH', page: 2, page_size: 25 });
  });

  it('blocks an invalid local period before calling the API', () => {
    const fixture = TestBed.createComponent(IncidentListPageComponent);
    const component = fixture.componentInstance;
    const api = TestBed.inject(IncidentApiService) as unknown as IncidentApiStub;
    fixture.detectChanges();
    const callsBefore = api.queries.length;

    component.startedFrom.setValue('2026-09-13T15:00');
    component.startedTo.setValue('2026-09-13T14:00');
    component.applyFilters(new Event('submit'));

    expect(api.queries.length).toBe(callsBefore);
    expect(component.error()).toContain('não pode ser posterior');
  });
});
