import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { ApiError } from '../../core/http/api-error';
import { AuditApiService } from './audit-api.service';
import { AuditEventPage } from './audit.model';

@Component({
  selector: 'app-audit-page',
  standalone: true,
  imports: [DatePipe],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="audit-title">
      <div class="header">
        <div>
          <p class="eyebrow">Governança</p>
          <h1 id="audit-title">Auditoria</h1>
          <p>Metadados de ações críticas do tenant ativo. Conteúdo operacional e credenciais não são registrados aqui.</p>
        </div>
        <button type="button" (click)="load()">Atualizar</button>
      </div>

      @if (loading()) {
        <p role="status">Carregando trilha de auditoria…</p>
      } @else if (error()) {
        <div class="state" role="alert">
          <strong>Não foi possível consultar a auditoria.</strong>
          <span>{{ error() }}</span>
          <button type="button" (click)="load()">Tentar novamente</button>
        </div>
      } @else if (data(); as result) {
        @if (result.items.length === 0) {
          <div class="state"><strong>Nenhum evento registrado.</strong><span>Ações críticas aparecerão aqui.</span></div>
        } @else {
          <div class="table-wrap">
            <table>
              <caption>{{ result.total }} evento(s) auditável(is)</caption>
              <thead><tr><th>Quando</th><th>Ação</th><th>Recurso</th><th>Ator</th><th>Request ID</th></tr></thead>
              <tbody>
                @for (item of result.items; track item.id) {
                  <tr>
                    <td>{{ item.occurred_at | date:'dd/MM/yyyy HH:mm:ss' }}</td>
                    <td><code>{{ item.action }}</code></td>
                    <td>{{ item.resource_type }} @if (item.resource_id) { <small>{{ item.resource_id }}</small> }</td>
                    <td>{{ item.actor_subject }}</td>
                    <td><code>{{ item.request_id }}</code></td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        }
      }
    </section>
  `,
  styles: `
    section { max-width:90rem; margin-inline:auto; }
    .header { display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; }
    .eyebrow { margin:0 0 .35rem; font-size:.8rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
    h1 { margin:.1rem 0; font-size:clamp(2rem,5vw,3rem); }
    button { border:1px solid currentColor; border-radius:.55rem; padding:.6rem .85rem; background:CanvasText; color:Canvas; font-weight:700; cursor:pointer; }
    .state { display:grid; gap:.5rem; padding:1rem; border:1px solid color-mix(in srgb, CanvasText 20%, transparent); border-radius:.8rem; }
    .table-wrap { overflow:auto; border:1px solid color-mix(in srgb, CanvasText 20%, transparent); border-radius:.8rem; }
    table { width:100%; border-collapse:collapse; min-width:54rem; }
    caption { text-align:left; padding:1rem; font-weight:700; }
    th,td { text-align:left; padding:.75rem; border-block-start:1px solid color-mix(in srgb, CanvasText 14%, transparent); vertical-align:top; }
    td small { display:block; opacity:.65; overflow-wrap:anywhere; max-width:18rem; }
    code { font-size:.82rem; overflow-wrap:anywhere; }
    @media (max-width:48rem) { .header { flex-direction:column; } }
  `,
})
export class AuditPageComponent implements OnInit {
  private readonly api = inject(AuditApiService);
  readonly data = signal<AuditEventPage | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.api.list().pipe(finalize(() => this.loading.set(false))).subscribe({
      next: (value) => this.data.set(value),
      error: (error: unknown) =>
        this.error.set(error instanceof ApiError ? error.message : 'Falha inesperada ao consultar a API.'),
    });
  }
}
