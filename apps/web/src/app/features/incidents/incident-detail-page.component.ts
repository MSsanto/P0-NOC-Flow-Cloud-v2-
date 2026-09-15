import { DatePipe } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { AuthContextService } from '../../core/auth/auth-context.service';
import { ApiError } from '../../core/http/api-error';
import { IncidentApiService } from './incident-api.service';
import { trimmedLength } from './incident-form.validators';
import { Incident, IncidentEvent, IncidentEventType } from './incident.model';

@Component({
  selector: 'app-incident-detail-page',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule, RouterLink],
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
          @if (!notFound()) {
            <button type="button" (click)="load()">Tentar novamente</button>
          }
        </div>
      } @else if (incident(); as item) {
        <div class="heading">
          <div>
            <p class="eyebrow">Detalhe do incidente</p>
            <h1 id="detail-title">{{ item.title }}</h1>
          </div>
          <div class="badges" aria-label="Classificação do incidente">
            <span>{{ item.severity }}</span><span>{{ item.status }}</span>
          </div>
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

        <div class="workspace">
          <section class="panel" aria-labelledby="actions-title">
            <div class="panel-heading">
              <div>
                <p class="eyebrow">Operação</p>
                <h2 id="actions-title">Ações do incidente</h2>
              </div>
              @if (!isActive()) {
                <span class="muted">Incidente encerrado para atualizações operacionais.</span>
              }
            </div>

            @if (actionSuccess()) {
              <p class="feedback success" role="status" aria-live="polite">{{ actionSuccess() }}</p>
            }
            @if (actionError()) {
              <p class="feedback error" role="alert">{{ actionError() }}</p>
            }

            @if (!canWrite()) {
              <p class="muted">Seu perfil possui acesso somente de leitura para este incidente.</p>
            } @else if (isActive()) {
              @if (canUpdate()) {
                <form (submit)="submitUpdate($event)" novalidate>
                  <label for="incident-update">Nova atualização</label>
                  <textarea
                    id="incident-update"
                    rows="5"
                    maxlength="2000"
                    [formControl]="updateMessage"
                    aria-describedby="update-help update-error"
                    placeholder="Ex.: Operadora acionada; protocolo DEMO-123."
                  ></textarea>
                  <div class="field-meta">
                    <small id="update-help">De 3 a 2000 caracteres após remover espaços extras.</small>
                    <small>{{ updateMessage.value.trim().length }}/2000</small>
                  </div>
                  @if (updateMessage.invalid && updateMessage.touched) {
                    <p id="update-error" class="field-error" role="alert">Informe uma atualização com pelo menos 3 caracteres.</p>
                  }
                  <div class="actions">
                    <button type="submit" [disabled]="submittingUpdate()">{{ submittingUpdate() ? 'Salvando…' : 'Adicionar atualização' }}</button>
                    @if (canNormalize()) {
                      <button type="button" class="secondary" (click)="openNormalize()">Normalizar incidente</button>
                    }
                  </div>
                </form>
              } @else if (canNormalize()) {
                <div class="actions">
                  <button type="button" class="secondary" (click)="openNormalize()">Normalizar incidente</button>
                </div>
              }

              @if (showNormalize() && canNormalize()) {
                <div class="normalize-box" role="region" aria-labelledby="normalize-title">
                  <h3 id="normalize-title">Confirmar normalização</h3>
                  <p>Confirme somente após validar que o serviço foi restabelecido. A ação altera o status para RESOLVED.</p>
                  <label for="normalize-note">Observação opcional</label>
                  <textarea
                    id="normalize-note"
                    rows="3"
                    maxlength="2000"
                    [formControl]="normalizeNote"
                    aria-describedby="normalize-error"
                    placeholder="Ex.: Energia restabelecida e conectividade validada."
                  ></textarea>
                  @if (normalizeNote.invalid && normalizeNote.touched) {
                    <p id="normalize-error" class="field-error" role="alert">A observação, quando informada, deve ter pelo menos 3 caracteres.</p>
                  }
                  <div class="actions">
                    <button type="button" class="danger" [disabled]="normalizing()" (click)="confirmNormalize()">
                      {{ normalizing() ? 'Normalizando…' : 'Confirmar normalização' }}
                    </button>
                    <button type="button" class="secondary" [disabled]="normalizing()" (click)="cancelNormalize()">Cancelar</button>
                  </div>
                </div>
              }
            }
          </section>

          <section class="panel" aria-labelledby="timeline-title">
            <div class="panel-heading">
              <div>
                <p class="eyebrow">Histórico</p>
                <h2 id="timeline-title">Timeline</h2>
              </div>
              <button type="button" class="secondary" [disabled]="timelineLoading()" (click)="loadTimeline(item.id)">Atualizar</button>
            </div>

            @if (timelineLoading()) {
              <p role="status" aria-live="polite">Carregando timeline…</p>
            } @else if (timelineError()) {
              <div class="state compact" role="alert">
                <span>{{ timelineError() }}</span>
                <button type="button" (click)="loadTimeline(item.id)">Tentar novamente</button>
              </div>
            } @else if (timeline().length === 0) {
              <p class="muted">Nenhum evento registrado para este incidente.</p>
            } @else {
              <ol class="timeline-list">
                @for (event of timeline(); track event.id) {
                  <li>
                    <span class="dot" aria-hidden="true"></span>
                    <div class="event-card">
                      <div class="event-heading">
                        <strong>{{ eventLabel(event.event_type) }}</strong>
                        <time [attr.datetime]="event.occurred_at">{{ event.occurred_at | date:'dd/MM/yyyy HH:mm:ss' }}</time>
                      </div>
                      <span class="actor">{{ event.actor_subject }}</span>
                      @if (event.message) { <p>{{ event.message }}</p> }
                    </div>
                  </li>
                }
              </ol>
            }
          </section>
        </div>
      }
    </section>
  `,
  styles: `
    section { max-width: 72rem; margin-inline: auto; }
    .heading { display: flex; justify-content: space-between; align-items: end; gap: 1rem; margin-block: 2rem; }
    .eyebrow { margin: 0 0 .35rem; font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    h1 { margin: 0; font-size: clamp(2rem, 5vw, 3rem); overflow-wrap: anywhere; }
    h2, h3 { margin: 0; }
    .badges { display: flex; gap: .5rem; flex-wrap: wrap; }
    .badges span { padding: .3rem .6rem; border: 1px solid currentColor; border-radius: 999px; font-size: .8rem; font-weight: 700; }
    dl { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }
    dl div { padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .65rem; min-width: 0; }
    dt { font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; }
    dd { margin: .4rem 0 0; overflow-wrap: anywhere; white-space: pre-wrap; }
    .wide { grid-column: 1 / -1; }
    .workspace { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); gap: 1rem; margin-block-start: 1rem; align-items: start; }
    .panel { padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .75rem; }
    .panel-heading { display: flex; justify-content: space-between; align-items: start; gap: 1rem; margin-block-end: 1rem; }
    form, .normalize-box { display: grid; gap: .65rem; }
    label { font-weight: 700; }
    textarea { width: 100%; box-sizing: border-box; resize: vertical; padding: .75rem; border: 1px solid color-mix(in srgb, CanvasText 35%, transparent); border-radius: .5rem; background: Canvas; color: CanvasText; font: inherit; }
    textarea:focus-visible, button:focus-visible, a:focus-visible { outline: 3px solid Highlight; outline-offset: 2px; }
    .field-meta, .event-heading { display: flex; justify-content: space-between; gap: .75rem; align-items: baseline; }
    .field-error, .feedback.error { color: #b42318; }
    .feedback.success { color: #067647; }
    .feedback { margin: 0 0 .75rem; font-weight: 700; }
    .actions { display: flex; flex-wrap: wrap; gap: .5rem; }
    button { width: fit-content; padding: .6rem .9rem; border: 1px solid currentColor; border-radius: .5rem; background: CanvasText; color: Canvas; font: inherit; font-weight: 700; cursor: pointer; }
    button.secondary { background: Canvas; color: CanvasText; }
    button.danger { background: #b42318; color: white; border-color: #b42318; }
    button:disabled { cursor: not-allowed; opacity: .55; }
    .normalize-box { margin-block-start: 1rem; padding: 1rem; border: 1px solid color-mix(in srgb, #b42318 55%, transparent); border-radius: .65rem; }
    .normalize-box p { margin: 0; }
    .timeline-list { list-style: none; margin: 0; padding: 0; display: grid; gap: .8rem; }
    .timeline-list li { position: relative; display: grid; grid-template-columns: 1rem minmax(0, 1fr); gap: .65rem; }
    .timeline-list li:not(:last-child)::before { content: ''; position: absolute; left: .45rem; top: 1rem; bottom: -.9rem; width: 1px; background: color-mix(in srgb, CanvasText 28%, transparent); }
    .dot { position: relative; z-index: 1; width: .65rem; height: .65rem; margin-block-start: .3rem; border-radius: 999px; background: CanvasText; }
    .event-card { min-width: 0; padding: .8rem; border: 1px solid color-mix(in srgb, CanvasText 18%, transparent); border-radius: .6rem; }
    .event-card p { margin: .55rem 0 0; white-space: pre-wrap; overflow-wrap: anywhere; }
    .event-heading time, .actor, .muted { color: color-mix(in srgb, CanvasText 66%, transparent); font-size: .85rem; }
    .actor { display: inline-block; margin-block-start: .2rem; }
    .state { display: grid; gap: .75rem; margin-block-start: 2rem; padding: 1rem; border: 1px solid currentColor; border-radius: .65rem; }
    .state.compact { margin-block-start: 0; }
    @media (max-width: 52rem) { .workspace { grid-template-columns: 1fr; } }
    @media (max-width: 40rem) { .heading, .panel-heading, .field-meta, .event-heading { align-items: stretch; flex-direction: column; } dl { grid-template-columns: 1fr; } .wide { grid-column: auto; } .actions button { width: 100%; } }
  `,
})
export class IncidentDetailPageComponent implements OnInit {
  private readonly api = inject(IncidentApiService);
  private readonly route = inject(ActivatedRoute);
  readonly auth = inject(AuthContextService);

  readonly incident = signal<Incident | null>(null);
  readonly timeline = signal<IncidentEvent[]>([]);
  readonly loading = signal(true);
  readonly timelineLoading = signal(false);
  readonly error = signal<string | null>(null);
  readonly timelineError = signal<string | null>(null);
  readonly actionError = signal<string | null>(null);
  readonly actionSuccess = signal<string | null>(null);
  readonly notFound = signal(false);
  readonly submittingUpdate = signal(false);
  readonly normalizing = signal(false);
  readonly showNormalize = signal(false);

  readonly updateMessage = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, trimmedLength(3, 2000)],
  });
  readonly normalizeNote = new FormControl('', {
    nonNullable: true,
    validators: [trimmedLength(3, 2000)],
  });

  readonly isActive = computed(() => {
    const status = this.incident()?.status;
    return status !== undefined && status !== 'RESOLVED' && status !== 'CLOSED';
  });
  readonly canUpdate = computed(() => this.auth.can('incident:update'));
  readonly canNormalize = computed(() => this.auth.can('incident:normalize'));
  readonly canWrite = computed(() => this.canUpdate() || this.canNormalize());

  ngOnInit(): void {
    this.load();
  }

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
    this.api
      .get(id)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (incident) => {
          this.incident.set(incident);
          this.loadTimeline(incident.id);
        },
        error: (error: unknown) => {
          this.notFound.set(error instanceof ApiError && error.status === 404);
          this.error.set(this.errorMessage(error, 'Falha inesperada ao consultar a API.'));
        },
      });
  }

  loadTimeline(id: string): void {
    this.timelineLoading.set(true);
    this.timelineError.set(null);
    this.api
      .timeline(id)
      .pipe(finalize(() => this.timelineLoading.set(false)))
      .subscribe({
        next: (events) => this.timeline.set(events),
        error: (error: unknown) =>
          this.timelineError.set(this.errorMessage(error, 'Falha inesperada ao carregar a timeline.')),
      });
  }

  submitUpdate(event: Event): void {
    event.preventDefault();
    if (!this.isActive() || !this.canUpdate()) return;
    if (this.updateMessage.invalid) {
      this.updateMessage.markAsTouched();
      return;
    }

    const incident = this.incident();
    if (!incident) return;

    this.actionError.set(null);
    this.actionSuccess.set(null);
    this.submittingUpdate.set(true);
    this.api
      .addUpdate(incident.id, { message: this.updateMessage.value.trim() })
      .pipe(finalize(() => this.submittingUpdate.set(false)))
      .subscribe({
        next: (updated) => {
          this.incident.set(updated);
          this.updateMessage.reset();
          this.actionSuccess.set('Atualização registrada na timeline.');
          this.loadTimeline(updated.id);
        },
        error: (error: unknown) =>
          this.actionError.set(this.errorMessage(error, 'Não foi possível registrar a atualização.')),
      });
  }

  openNormalize(): void {
    if (!this.isActive() || !this.canNormalize()) return;
    this.actionError.set(null);
    this.actionSuccess.set(null);
    this.showNormalize.set(true);
  }

  cancelNormalize(): void {
    this.showNormalize.set(false);
    this.normalizeNote.reset();
  }

  confirmNormalize(): void {
    if (!this.isActive() || !this.canNormalize()) return;
    if (this.normalizeNote.invalid) {
      this.normalizeNote.markAsTouched();
      return;
    }

    const incident = this.incident();
    if (!incident) return;

    const note = this.normalizeNote.value.trim();
    this.actionError.set(null);
    this.actionSuccess.set(null);
    this.normalizing.set(true);
    this.api
      .normalize(incident.id, note ? { note } : {})
      .pipe(finalize(() => this.normalizing.set(false)))
      .subscribe({
        next: (normalized) => {
          this.incident.set(normalized);
          this.showNormalize.set(false);
          this.normalizeNote.reset();
          this.actionSuccess.set('Incidente normalizado com sucesso.');
          this.loadTimeline(normalized.id);
        },
        error: (error: unknown) =>
          this.actionError.set(this.errorMessage(error, 'Não foi possível normalizar o incidente.')),
      });
  }

  eventLabel(type: IncidentEventType): string {
    switch (type) {
      case 'INCIDENT_CREATED':
        return 'Incidente criado';
      case 'INCIDENT_UPDATED':
        return 'Atualização registrada';
      case 'INCIDENT_NORMALIZED':
        return 'Incidente normalizado';
    }
  }

  private errorMessage(error: unknown, fallback: string): string {
    return error instanceof ApiError ? error.message : fallback;
  }
}
