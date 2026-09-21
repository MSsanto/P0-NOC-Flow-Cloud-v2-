import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { ApiError } from '../../core/http/api-error';
import { OperationsApiService } from './operations-api.service';
import { DashboardSummary } from './operations.model';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [DatePipe, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="dashboard-title">
      <div class="page-header">
        <div>
          <p class="eyebrow">Operação</p>
          <h1 id="dashboard-title">Dashboard</h1>
        </div>
        <a class="secondary" routerLink="/handovers">Passagem de turno</a>
      </div>

      @if (loading()) {
        <p role="status" aria-live="polite">Carregando situação operacional…</p>
      } @else if (error()) {
        <div class="state error" role="alert">
          <strong>Não foi possível carregar o dashboard.</strong>
          <span>{{ error() }}</span>
          <button type="button" (click)="load()">Tentar novamente</button>
        </div>
      } @else if (summary(); as data) {
        <p class="shift">
          Turno atual: {{ data.shift.window_start | date:'dd/MM HH:mm' }} →
          {{ data.shift.window_end | date:'dd/MM HH:mm' }}
        </p>

        <div class="cards" aria-label="Resumo do plantão">
          <a routerLink="/incidents" [queryParams]="{ status: 'active' }">
            <span>Incidentes ativos</span><strong>{{ data.active_count }}</strong>
          </a>
          <a routerLink="/incidents" [queryParams]="{ severity: 'CRITICAL' }">
            <span>Críticos ativos</span><strong>{{ data.critical_active_count }}</strong>
          </a>
          <a routerLink="/incidents" [queryParams]="{ status: 'RESOLVED' }">
            <span>Normalizados no turno</span><strong>{{ data.resolved_in_shift_count }}</strong>
          </a>
        </div>

        <h2>Fila ativa</h2>
        @if (data.items.length === 0) {
          <div class="state"><strong>Nenhum incidente ativo.</strong><span>O plantão está sem incidentes abertos neste momento.</span></div>
        } @else {
          <ul class="queue">
            @for (item of data.items; track item.id) {
              <li>
                <a [routerLink]="['/incidents', item.id]">
                  <div><strong>{{ item.title }}</strong><span class="badge">{{ item.severity }}</span></div>
                  <span>{{ item.affected_resource }} · {{ item.status }}</span>
                  <small>Desde {{ item.started_at | date:'dd/MM/yyyy HH:mm' }}</small>
                </a>
              </li>
            }
          </ul>
        }
      }
    </section>
  `,
  styles: `
    section { max-width: 72rem; margin-inline: auto; }
    .page-header, .queue a div { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
    .page-header { margin-block-end:1rem; }
    .eyebrow { margin:0 0 .35rem; font-size:.8rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
    h1 { margin:0; font-size:clamp(2rem,5vw,3rem); }
    h2 { margin-block-start:2rem; }
    .shift, small, .state span { opacity:.75; }
    .cards { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; }
    .cards a, .queue a, .state { border:1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius:.85rem; color:inherit; text-decoration:none; }
    .cards a { display:grid; gap:.5rem; padding:1rem; }
    .cards strong { font-size:2rem; }
    .queue { list-style:none; padding:0; display:grid; gap:.75rem; }
    .queue a { display:grid; gap:.45rem; padding:1rem; }
    .badge { border:1px solid currentColor; border-radius:999px; padding:.2rem .5rem; font-size:.75rem; font-weight:700; }
    .state { display:grid; gap:.65rem; padding:1rem; }
    .secondary, button { border:1px solid currentColor; border-radius:.55rem; padding:.65rem .9rem; background:Canvas; color:CanvasText; text-decoration:none; font-weight:700; cursor:pointer; }
    @media (max-width:48rem) { .cards { grid-template-columns:1fr; } .page-header { align-items:stretch; flex-direction:column; } }
  `,
})
export class DashboardPageComponent implements OnInit {
  private readonly api = inject(OperationsApiService);
  readonly summary = signal<DashboardSummary | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.dashboard().pipe(finalize(() => this.loading.set(false))).subscribe({
      next: (value) => this.summary.set(value),
      error: (error: unknown) => this.error.set(
        error instanceof ApiError ? error.message : 'Falha inesperada ao consultar a API.',
      ),
    });
  }
}
