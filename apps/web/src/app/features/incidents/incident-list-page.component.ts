import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { ApiError } from '../../core/http/api-error';
import { IncidentApiService } from './incident-api.service';
import { Incident } from './incident.model';

@Component({
  selector: 'app-incident-list-page',
  standalone: true,
  imports: [DatePipe, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="incidents-title">
      <div class="page-header">
        <div><p class="eyebrow">Operação</p><h1 id="incidents-title">Incidentes</h1></div>
        <a class="primary" routerLink="/incidents/new">Registrar incidente</a>
      </div>

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
          <strong>Nenhum incidente registrado.</strong>
          <span>A operação está sem incidentes no contexto atual.</span>
          <a routerLink="/incidents/new">Registrar o primeiro incidente</a>
        </div>
      } @else {
        <ul class="incident-list" aria-label="Incidentes registrados">
          @for (incident of incidents(); track incident.id) {
            <li>
              <a [routerLink]="['/incidents', incident.id]">
                <div class="card-top">
                  <strong>{{ incident.title }}</strong>
                  <span class="badge">{{ incident.severity }}</span>
                </div>
                <span>{{ incident.affected_resource }} · {{ incident.status }}</span>
                <small>Início: {{ incident.started_at | date:'dd/MM/yyyy HH:mm' }} · ID {{ incident.id }}</small>
              </a>
            </li>
          }
        </ul>
      }
    </section>
  `,
  styles: `
    section { max-width: 72rem; margin-inline: auto; }
    .page-header, .card-top { display: flex; justify-content: space-between; align-items: center; gap: 1rem; }
    .page-header { margin-block-end: 2rem; align-items: end; }
    .eyebrow { margin: 0 0 .35rem; font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    h1 { margin: 0; font-size: clamp(2rem, 5vw, 3rem); }
    .primary, button { display: inline-block; border: 1px solid currentColor; border-radius: .5rem; padding: .7rem 1rem; font: inherit; font-weight: 700; background: CanvasText; color: Canvas; cursor: pointer; text-decoration: none; }
    .incident-list { list-style: none; padding: 0; display: grid; gap: .75rem; }
    .incident-list a { display: grid; gap: .5rem; padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .75rem; color: inherit; text-decoration: none; }
    .incident-list a:hover, .incident-list a:focus-visible { border-color: currentColor; }
    .badge { padding: .25rem .5rem; border: 1px solid currentColor; border-radius: 999px; font-size: .75rem; font-weight: 700; }
    small, .state span { opacity: .78; overflow-wrap: anywhere; }
    .state { display: grid; gap: .75rem; padding: 1.25rem; border: 1px dashed currentColor; border-radius: .75rem; }
    .error { border-style: solid; }
    @media (max-width: 40rem) { .page-header, .card-top { align-items: stretch; flex-direction: column; } }
  `,
})
export class IncidentListPageComponent implements OnInit {
  private readonly api = inject(IncidentApiService);
  readonly incidents = signal<Incident[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list().pipe(finalize(() => this.loading.set(false))).subscribe({
      next: (items) => this.incidents.set(items),
      error: (error: unknown) => this.error.set(error instanceof ApiError ? error.message : 'Falha inesperada ao consultar a API.'),
    });
  }
}
