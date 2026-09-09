import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';

import { ApiError } from '../../core/http/api-error';
import { IncidentApiService } from './incident-api.service';
import { localDateTimeMax, notFutureDateTime, trimmedLength } from './incident-form.validators';
import { IncidentCreateRequest, IncidentImpactType, IncidentSeverity } from './incident.model';

@Component({
  selector: 'app-incident-create-page',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="create-title">
      <a routerLink="/incidents">← Voltar para incidentes</a>
      <p class="eyebrow">Registro operacional</p>
      <h1 id="create-title">Novo incidente</h1>
      <p>Informe apenas dados operacionais. Tenant, autor, ID e status inicial são definidos pelo sistema.</p>

      @if (error()) { <div class="error" role="alert"><strong>Não foi possível criar.</strong><span>{{ error() }}</span></div> }

      <form [formGroup]="form" (ngSubmit)="submit()" novalidate>
        <label>Título/resumo
          <input formControlName="title" maxlength="120" autocomplete="off" />
          <small>3–120 caracteres úteis.</small>
        </label>

        <label>Recurso ou serviço afetado
          <input formControlName="affected_resource" maxlength="120" autocomplete="off" />
          <small>2–120 caracteres úteis.</small>
        </label>

        <div class="row">
          <label>Severidade
            <select formControlName="severity">
              @for (option of severities; track option) { <option [value]="option">{{ option }}</option> }
            </select>
          </label>
          <label>Tipo de impacto
            <select formControlName="impact_type">
              @for (option of impactTypes; track option) { <option [value]="option">{{ option }}</option> }
            </select>
          </label>
        </div>

        <label>Sintomas / descrição
          <textarea formControlName="symptoms" maxlength="2000" rows="6"></textarea>
          <small>10–2000 caracteres úteis.</small>
        </label>

        <label>Início do incidente
          <input type="datetime-local" formControlName="started_at" [max]="maxStartedAt" />
          <small>Não pode estar no futuro.</small>
        </label>

        @if (form.invalid && form.touched) {
          <p class="validation" role="alert">Revise os campos obrigatórios, espaços em branco, limites e a data de início.</p>
        }

        <div class="actions">
          <button type="submit" [disabled]="submitting()">{{ submitting() ? 'Registrando…' : 'Registrar incidente' }}</button>
          <a routerLink="/incidents">Cancelar</a>
        </div>
      </form>
    </section>
  `,
  styles: `
    section { max-width: 48rem; margin-inline: auto; }
    .eyebrow { margin: 2rem 0 .35rem; font-size: .8rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
    h1 { margin: 0; font-size: clamp(2rem, 5vw, 3rem); }
    form { display: grid; gap: 1rem; margin-block-start: 2rem; }
    label { display: grid; gap: .4rem; font-weight: 700; }
    input, select, textarea { width: 100%; box-sizing: border-box; padding: .7rem; border: 1px solid color-mix(in srgb, CanvasText 40%, transparent); border-radius: .45rem; background: Canvas; color: CanvasText; font: inherit; }
    textarea { resize: vertical; }
    small { font-weight: 400; opacity: .75; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
    .actions { display: flex; align-items: center; gap: 1rem; margin-block-start: .5rem; }
    button { border: 1px solid currentColor; border-radius: .5rem; padding: .75rem 1rem; background: CanvasText; color: Canvas; font: inherit; font-weight: 700; cursor: pointer; }
    button:disabled { opacity: .6; cursor: progress; }
    .error, .validation { display: grid; gap: .35rem; padding: 1rem; border: 1px solid currentColor; border-radius: .5rem; }
    @media (max-width: 40rem) { .row { grid-template-columns: 1fr; } .actions { align-items: stretch; flex-direction: column; } }
  `,
})
export class IncidentCreatePageComponent {
  private readonly fb = inject(FormBuilder);
  private readonly api = inject(IncidentApiService);
  private readonly router = inject(Router);

  readonly severities: IncidentSeverity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
  readonly impactTypes: IncidentImpactType[] = ['OUTAGE', 'DEGRADATION'];
  readonly submitting = signal(false);
  readonly error = signal<string | null>(null);
  readonly maxStartedAt = localDateTimeMax();

  readonly form = this.fb.nonNullable.group({
    title: ['', [Validators.required, trimmedLength(3, 120)]],
    affected_resource: ['', [Validators.required, trimmedLength(2, 120)]],
    severity: ['HIGH' as IncidentSeverity, Validators.required],
    impact_type: ['OUTAGE' as IncidentImpactType, Validators.required],
    symptoms: ['', [Validators.required, trimmedLength(10, 2000)]],
    started_at: ['', [Validators.required, notFutureDateTime]],
  });

  submit(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid || this.submitting()) return;

    const value = this.form.getRawValue();
    const startedAt = new Date(value.started_at);
    if (Number.isNaN(startedAt.getTime()) || startedAt.getTime() > Date.now()) {
      this.form.controls.started_at.updateValueAndValidity();
      return;
    }

    const payload: IncidentCreateRequest = {
      ...value,
      title: value.title.trim(),
      affected_resource: value.affected_resource.trim(),
      symptoms: value.symptoms.trim(),
      started_at: startedAt.toISOString(),
    };
    this.error.set(null);
    this.submitting.set(true);
    this.api.create(payload).pipe(finalize(() => this.submitting.set(false))).subscribe({
      next: (incident) => void this.router.navigate(['/incidents', incident.id]),
      error: (error: unknown) => this.error.set(error instanceof ApiError ? error.message : 'Falha inesperada ao registrar o incidente.'),
    });
  }
}
