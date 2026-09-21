import { DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize, forkJoin } from 'rxjs';

import { AuthContextService } from '../../core/auth/auth-context.service';
import { ApiError } from '../../core/http/api-error';
import { OperationsApiService } from './operations-api.service';
import { Handover, HandoverHistory, HandoverPreview } from './operations.model';

@Component({
  selector: 'app-handover-page',
  standalone: true,
  imports: [DatePipe, ReactiveFormsModule, RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="handover-title">
      <div class="page-header">
        <div><p class="eyebrow">Operação</p><h1 id="handover-title">Passagem de turno</h1></div>
        <a class="secondary" routerLink="/dashboard">Dashboard</a>
      </div>

      @if (loading()) {
        <p role="status" aria-live="polite">Carregando passagem de turno…</p>
      } @else if (error()) {
        <div class="state error" role="alert">
          <strong>Não foi possível carregar a passagem.</strong><span>{{ error() }}</span>
          <button type="button" (click)="load()">Tentar novamente</button>
        </div>
      } @else {
        @if (preview(); as data) {
          <div class="panel">
            <div class="panel-head">
              <div>
                <h2>Prévia do turno atual</h2>
                <small>{{ data.window_start | date:'dd/MM HH:mm' }} → {{ data.window_end | date:'dd/MM HH:mm' }}</small>
              </div>
              <span class="badge">{{ data.items.length }} item(ns)</span>
            </div>

            @if (data.items.length === 0) {
              <p>Nenhum incidente selecionado. É possível finalizar o turno vazio para registrar explicitamente essa condição.</p>
            } @else {
              <ul class="items">
                @for (item of data.items; track item.incident_id) {
                  <li>
                    <a [routerLink]="['/incidents', item.incident_id]"><strong>{{ item.title }}</strong></a>
                    <span>{{ item.affected_resource }} · {{ item.severity }} · {{ item.status }}</span>
                    @if (item.last_event_message) { <small>{{ item.last_event_message }}</small> }
                  </li>
                }
              </ul>
            }

            @if (auth.can('handover:finalize')) {
              <label for="observations">Observações gerais</label>
              <textarea id="observations" rows="4" maxlength="4000" [formControl]="observations"></textarea>
              @if (observations.invalid && observations.touched) {
                <small role="alert">Use pelo menos 3 caracteres ou deixe o campo vazio.</small>
              }
              <button type="button" [disabled]="submitting() || observations.invalid" (click)="finalizeHandover()">
                {{ submitting() ? 'Finalizando…' : 'Finalizar passagem' }}
              </button>
            }
          </div>
        }

        @if (latest(); as item) {
          <article class="panel">
            <div class="panel-head">
              <div><h2>Última passagem finalizada</h2><small>Versão {{ item.version }} · {{ item.finalized_at | date:'dd/MM/yyyy HH:mm' }}</small></div>
              <span class="badge">{{ item.items.length }} item(ns)</span>
            </div>
            <p><strong>Responsável:</strong> {{ item.finalized_by_subject }}</p>
            @if (item.observations) { <p>{{ item.observations }}</p> }
          </article>
        } @else {
          <div class="state"><strong>Nenhuma passagem finalizada.</strong><span>O histórico será criado na primeira finalização.</span></div>
        }

        @if (history(); as list) {
          @if (list.items.length > 0) {
            <h2>Histórico</h2>
            <ul class="history">
              @for (item of list.items; track item.id) {
                <li><button type="button" class="link-button" (click)="openVersion(item.id)">Versão {{ item.version }} · {{ item.finalized_at | date:'dd/MM/yyyy HH:mm' }} · {{ item.finalized_by_subject }}</button></li>
              }
            </ul>
          }
        }
      }
    </section>
  `,
  styles: `
    section { max-width:72rem; margin-inline:auto; }
    .page-header,.panel-head { display:flex; justify-content:space-between; align-items:center; gap:1rem; }
    .page-header { margin-block-end:1rem; }
    .eyebrow { margin:0 0 .35rem; font-size:.8rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
    h1 { margin:0; font-size:clamp(2rem,5vw,3rem); } h2 { margin:.2rem 0; }
    .panel,.state { border:1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius:.85rem; padding:1rem; margin-block:1rem; }
    .items,.history { list-style:none; padding:0; display:grid; gap:.65rem; }
    .items li { display:grid; gap:.25rem; padding-block:.5rem; border-block-end:1px solid color-mix(in srgb, CanvasText 14%, transparent); }
    .items a { color:inherit; }
    label { display:block; font-weight:700; margin-block:.85rem .35rem; }
    textarea { width:100%; padding:.7rem; border:1px solid color-mix(in srgb, CanvasText 30%, transparent); border-radius:.55rem; background:Canvas; color:CanvasText; resize:vertical; }
    button,.secondary { display:inline-block; border:1px solid currentColor; border-radius:.55rem; padding:.65rem .9rem; background:CanvasText; color:Canvas; text-decoration:none; font-weight:700; cursor:pointer; margin-block-start:.65rem; }
    .secondary,.link-button { background:Canvas; color:CanvasText; }
    .link-button { text-align:left; margin:0; width:100%; }
    .badge { border:1px solid currentColor; border-radius:999px; padding:.2rem .5rem; font-size:.75rem; font-weight:700; }
    small,.state span { opacity:.75; }
    .state { display:grid; gap:.55rem; }
    @media (max-width:48rem) { .page-header,.panel-head { align-items:stretch; flex-direction:column; } }
  `,
})
export class HandoverPageComponent implements OnInit {
  private readonly api = inject(OperationsApiService);
  readonly auth = inject(AuthContextService);
  readonly preview = signal<HandoverPreview | null>(null);
  readonly latest = signal<Handover | null>(null);
  readonly history = signal<HandoverHistory | null>(null);
  readonly loading = signal(true);
  readonly submitting = signal(false);
  readonly error = signal<string | null>(null);
  readonly observations = new FormControl('', {
    nonNullable: true,
    validators: [Validators.pattern(/^$|.{3,}$/s), Validators.maxLength(4000)],
  });

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      preview: this.api.preview(),
      history: this.api.history(),
    }).pipe(finalize(() => this.loading.set(false))).subscribe({
      next: ({ preview, history }) => {
        this.preview.set(preview);
        this.history.set(history);
        if (history.items.length > 0) {
          this.api.latest().subscribe({ next: (value) => this.latest.set(value) });
        } else {
          this.latest.set(null);
        }
      },
      error: (error: unknown) => this.error.set(this.message(error)),
    });
  }

  finalizeHandover(): void {
    this.observations.markAsTouched();
    if (this.observations.invalid || !confirm('Finalizar esta passagem? O snapshot será imutável.')) return;
    this.submitting.set(true);
    this.error.set(null);
    this.api.finalize(this.observations.value.trim() || undefined)
      .pipe(finalize(() => this.submitting.set(false)))
      .subscribe({
        next: (value) => {
          this.latest.set(value);
          this.observations.setValue('');
          this.load();
        },
        error: (error: unknown) => this.error.set(this.message(error)),
      });
  }

  openVersion(id: string): void {
    this.api.get(id).subscribe({
      next: (value) => this.latest.set(value),
      error: (error: unknown) => this.error.set(this.message(error)),
    });
  }

  private message(error: unknown): string {
    return error instanceof ApiError ? error.message : 'Falha inesperada ao consultar a API.';
  }
}
