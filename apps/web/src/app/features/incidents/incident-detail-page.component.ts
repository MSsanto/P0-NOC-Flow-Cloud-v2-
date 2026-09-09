import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { ApiError } from '../../core/http/api-error';
import { IncidentApiService } from './incident-api.service';
import { Incident } from './incident.model';

@Component({
  selector: 'app-incident-detail-page',
  standalone: true,
  imports: [DatePipe, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="detail-title">
      <a routerLink="/incidents">← Voltar para incidentes</a>

      @if (loading()) {
        <p role="status" aria-live="polite">Carregando incidente…</p>
      } @else if (error()) {
        <div class="state" role="alert">
          <strong>{{ notFound() ? 'Incidente não encontrado.' : 'Não foi possível carregar o incidente.' }}</strong>
          <span>{{ error() }}</span>
          @if (!notFound()) { <button type="button" (click)="load()">Tentar novamente</button> }
        </div>
      } @else if (incident(); as item) {
        <div class="heading">
          <div><p class="eyebrow">Detalhe do incidente</p><h1 id="detail-title">{{ item.title }}</h1></div>
          <div class="badges"><span>{{ item.severity }}</span><span>{{ item.status }}</span></div>
        </div>

        <dl>
          <div><dt>ID</dt><dd>{{ item.id }}</dd></div>
          <div><dt>Recurso afetado</dt><dd>{{ item.affected_resource }}</dd></div>
          <div><dt>Tipo de impacto</dt><dd>{{ item.impact_type }}</dd></div>
          <div><dt>Início</dt><dd>{{ item.started_at | date:'dd/MM/yyyy HH:mm:ss' }}</dd></div>
          <div><dt>Criado em</dt><dd>{{ item.created_at | date:'dd/MM/yyyy HH:mm:ss' }}</dd></div>
          <div><dt>Atualizado em</dt><dd>{{ item.updated_at | date:'dd/MM/yyyy HH:mm:ss' }}</dd></div>
          <div class="wide"><dt>Sintomas / descrição</dt><dd>{{ item.symptoms }}</dd></div>
        </dl>
      }
    </section>
  `,
  styles: `
    section { max-width: 72rem; margin-inline: auto; }
    .heading { display: flex; justify-content: space-between; align-items: end; gap: 1rem; margin-block: 2rem; }
    .eyebrow { margin: 0 0 .35rem; font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    h1 { margin: 0; font-size: clamp(2rem, 5vw, 3rem); overflow-wrap: anywhere; }
    .badges { display: flex; gap: .5rem; flex-wrap: wrap; }
    .badges span { padding: .3rem .6rem; border: 1px solid currentColor; border-radius: 999px; font-size: .8rem; font-weight: 700; }
    dl { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }
    dl div { padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .65rem; min-width: 0; }
    dt { font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; }
    dd { margin: .4rem 0 0; overflow-wrap: anywhere; white-space: pre-wrap; }
    .wide { grid-column: 1 / -1; }
    .state { display: grid; gap: .75rem; margin-block-start: 2rem; padding: 1rem; border: 1px solid currentColor; border-radius: .65rem; }
    button { width: fit-content; padding: .6rem .9rem; border: 1px solid currentColor; border-radius: .5rem; background: CanvasText; color: Canvas; font: inherit; font-weight: 700; cursor: pointer; }
    @media (max-width: 40rem) { .heading { align-items: stretch; flex-direction: column; } dl { grid-template-columns: 1fr; } .wide { grid-column: auto; } }
  `,
})
export class IncidentDetailPageComponent implements OnInit {
  private readonly api = inject(IncidentApiService);
  private readonly route = inject(ActivatedRoute);
  readonly incident = signal<Incident | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly notFound = signal(false);

  ngOnInit(): void { this.load(); }

  load(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (!id) {
      this.loading.set(false);
      this.notFound.set(true);
      this.error.set('Identificador do incidente ausente.');
      return;
    }
    this.loading.set(true);
    this.error.set(null);
    this.notFound.set(false);
    this.api.get(id).pipe(finalize(() => this.loading.set(false))).subscribe({
      next: (incident) => this.incident.set(incident),
      error: (error: unknown) => {
        this.notFound.set(error instanceof ApiError && error.status === 404);
        this.error.set(error instanceof ApiError ? error.message : 'Falha inesperada ao consultar a API.');
      },
    });
  }
}
