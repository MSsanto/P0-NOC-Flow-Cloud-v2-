import { DatePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { ApiError } from '../../core/http/api-error';
import { IncidentApiService } from './incident-api.service';
import {
  IncidentListQuery,
  IncidentSortField,
  SortOrder,
} from './incident-query.model';
import { Incident, IncidentSeverity, IncidentStatus } from './incident.model';

type SortOption = `${IncidentSortField}:${SortOrder}`;

@Component({
  selector: 'app-incident-list-page',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="incidents-title">
      <div class="page-header">
        <div><p class="eyebrow">Operação</p><h1 id="incidents-title">Incidentes</h1></div>
        <a class="primary" routerLink="/incidents/new">Registrar incidente</a>
      </div>

      <form class="filters" aria-label="Filtros de incidentes" (submit)="applyFilters($event)">
        <div class="field">
          <label for="status-filter">Status</label>
          <select id="status-filter" [formControl]="statusFilter">
            <option value="">Todos</option>
            <option value="OPEN">OPEN</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
            <option value="INVESTIGATING">INVESTIGATING</option>
            <option value="MONITORING">MONITORING</option>
            <option value="RESOLVED">RESOLVED</option>
            <option value="CLOSED">CLOSED</option>
          </select>
        </div>

        <div class="field">
          <label for="severity-filter">Severidade</label>
          <select id="severity-filter" [formControl]="severityFilter">
            <option value="">Todas</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>
        </div>

        <div class="field">
          <label for="started-from">Início do período</label>
          <input id="started-from" type="datetime-local" [formControl]="startedFrom" />
        </div>

        <div class="field">
          <label for="started-to">Fim do período</label>
          <input id="started-to" type="datetime-local" [formControl]="startedTo" />
        </div>

        <div class="field">
          <label for="sort-filter">Ordenação</label>
          <select id="sort-filter" [formControl]="sortOption">
            <option value="started_at:desc">Início — mais recente</option>
            <option value="started_at:asc">Início — mais antigo</option>
            <option value="updated_at:desc">Atualização — mais recente</option>
            <option value="updated_at:asc">Atualização — mais antiga</option>
          </select>
        </div>

        <div class="filter-actions">
          <button type="submit">Aplicar filtros</button>
          <button type="button" class="secondary" (click)="clearFilters()">Limpar</button>
        </div>
      </form>

      @if (loading()) {
        <p role="status" aria-live="polite">Carregando incidentes…</p>
      } @else if (error()) {
        <div class="state error" role="alert">
          <strong>Não foi possível carregar os incidentes.</strong>
          <span>{{ error() }}</span>
          <button type="button" (click)="load()">Tentar novamente</button>
        </div>
      } @else if (incidents().length === 0) {
        <div class="state">
          <strong>Nenhum incidente encontrado.</strong>
          <span>Ajuste os filtros ou registre um novo incidente.</span>
          <a routerLink="/incidents/new">Registrar incidente</a>
        </div>
      } @else {
        <div class="results-meta" role="status" aria-live="polite">
          <span>Exibindo {{ firstItem() }}–{{ lastItem() }} de {{ total() }}</span>
          <span>Página {{ page() }} de {{ totalPages() }}</span>
        </div>

        <ul class="incident-list" aria-label="Incidentes registrados">
          @for (incident of incidents(); track incident.id) {
            <li>
              <a [routerLink]="['/incidents', incident.id]">
                <div class="card-top">
                  <strong>{{ incident.title }}</strong>
                  <span class="badge">{{ incident.severity }}</span>
                </div>
                <span>{{ incident.affected_resource }} · {{ incident.status }}</span>
                <small>
                  Início: {{ incident.started_at | date:'dd/MM/yyyy HH:mm' }} ·
                  Atualizado: {{ incident.updated_at | date:'dd/MM/yyyy HH:mm' }} ·
                  ID {{ incident.id }}
                </small>
              </a>
            </li>
          }
        </ul>

        <nav class="pagination" aria-label="Paginação de incidentes">
          <button
            type="button"
            class="secondary"
            [disabled]="!hasPrevious() || loading()"
            (click)="previousPage()"
          >
            ← Anterior
          </button>
          <button
            type="button"
            class="secondary"
            [disabled]="!hasNext() || loading()"
            (click)="nextPage()"
          >
            Próxima →
          </button>
        </nav>
      }
    </section>
  `,
  styles: `
    section { max-width: 72rem; margin-inline: auto; }
    .page-header, .card-top, .results-meta, .pagination { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
    .page-header { margin-block-end: 1.25rem; align-items: end; }
    .eyebrow { margin: 0 0 .35rem; font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    h1 { margin: 0; font-size: clamp(2rem, 5vw, 3rem); }
    .primary, button { display: inline-block; border: 1px solid currentColor; border-radius: .5rem; padding: .7rem 1rem; font: inherit; font-weight: 700; background: CanvasText; color: Canvas; cursor: pointer; text-decoration: none; }
    button.secondary { background: Canvas; color: CanvasText; }
    button:disabled { cursor: not-allowed; opacity: .5; }
    .filters { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: .75rem; margin-block-end: 1.25rem; padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .75rem; }
    .field { display: grid; align-content: start; gap: .35rem; min-width: 0; }
    label { font-size: .8rem; font-weight: 700; }
    select, input { min-width: 0; width: 100%; box-sizing: border-box; padding: .65rem; border: 1px solid color-mix(in srgb, CanvasText 32%, transparent); border-radius: .5rem; background: Canvas; color: CanvasText; font: inherit; }
    select:focus-visible, input:focus-visible, button:focus-visible, a:focus-visible { outline: 3px solid Highlight; outline-offset: 2px; }
    .filter-actions { grid-column: 1 / -1; display: flex; gap: .5rem; flex-wrap: wrap; }
    .results-meta { margin-block: .75rem; font-size: .9rem; }
    .incident-list { list-style: none; padding: 0; display: grid; gap: .75rem; }
    .incident-list a { display: grid; gap: .5rem; padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .75rem; color: inherit; text-decoration: none; }
    .incident-list a:hover, .incident-list a:focus-visible { border-color: currentColor; }
    .badge { padding: .25rem .5rem; border: 1px solid currentColor; border-radius: 999px; font-size: .75rem; font-weight: 700; }
    small, .state span, .results-meta { opacity: .78; overflow-wrap: anywhere; }
    .state { display: grid; gap: .75rem; padding: 1.25rem; border: 1px dashed currentColor; border-radius: .75rem; }
    .error { border-style: solid; }
    .pagination { margin-block-start: 1rem; justify-content: flex-end; }
    @media (max-width: 64rem) { .filters { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
    @media (max-width: 40rem) { .page-header, .card-top, .results-meta, .pagination { align-items: stretch; flex-direction: column; } .filters { grid-template-columns: 1fr; } .filter-actions button, .pagination button { width: 100%; } }
  `,
})
export class IncidentListPageComponent implements OnInit {
  private readonly api = inject(IncidentApiService);
  private readonly pageSize = 25;

  readonly incidents = signal<Incident[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly page = signal(1);
  readonly total = signal(0);

  readonly statusFilter = new FormControl<IncidentStatus | ''>('', { nonNullable: true });
  readonly severityFilter = new FormControl<IncidentSeverity | ''>('', { nonNullable: true });
  readonly startedFrom = new FormControl('', { nonNullable: true });
  readonly startedTo = new FormControl('', { nonNullable: true });
  readonly sortOption = new FormControl<SortOption>('started_at:desc', { nonNullable: true });

  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.total() / this.pageSize)));
  readonly hasPrevious = computed(() => this.page() > 1);
  readonly hasNext = computed(() => this.page() < this.totalPages());
  readonly firstItem = computed(() =>
    this.total() === 0 ? 0 : (this.page() - 1) * this.pageSize + 1,
  );
  readonly lastItem = computed(() => Math.min(this.page() * this.pageSize, this.total()));

  ngOnInit(): void {
    this.load();
  }

  load(targetPage = this.page()): void {
    const query = this.buildQuery(targetPage);
    if (!query) return;

    this.loading.set(true);
    this.error.set(null);
    this.api
      .list(query)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (result) => {
          this.incidents.set(result.items);
          this.page.set(result.page);
          this.total.set(result.total);
        },
        error: (error: unknown) =>
          this.error.set(
            error instanceof ApiError ? error.message : 'Falha inesperada ao consultar a API.',
          ),
      });
  }

  applyFilters(event: Event): void {
    event.preventDefault();
    this.page.set(1);
    this.load(1);
  }

  clearFilters(): void {
    this.statusFilter.setValue('');
    this.severityFilter.setValue('');
    this.startedFrom.setValue('');
    this.startedTo.setValue('');
    this.sortOption.setValue('started_at:desc');
    this.page.set(1);
    this.load(1);
  }

  previousPage(): void {
    if (this.hasPrevious()) this.load(this.page() - 1);
  }

  nextPage(): void {
    if (this.hasNext()) this.load(this.page() + 1);
  }

  private buildQuery(targetPage: number): IncidentListQuery | null {
    const startedFrom = this.toIso(this.startedFrom.value);
    const startedTo = this.toIso(this.startedTo.value);
    if (startedFrom && startedTo && startedFrom > startedTo) {
      this.loading.set(false);
      this.error.set('O início do período não pode ser posterior ao fim do período.');
      return null;
    }

    const [sort, order] = this.sortOption.value.split(':') as [IncidentSortField, SortOrder];
    return {
      page: targetPage,
      page_size: this.pageSize,
      sort,
      order,
      ...(this.statusFilter.value ? { status: this.statusFilter.value } : {}),
      ...(this.severityFilter.value ? { severity: this.severityFilter.value } : {}),
      ...(startedFrom ? { started_from: startedFrom } : {}),
      ...(startedTo ? { started_to: startedTo } : {}),
    };
  }

  private toIso(value: string): string | undefined {
    if (!value) return undefined;
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? undefined : parsed.toISOString();
  }
}
