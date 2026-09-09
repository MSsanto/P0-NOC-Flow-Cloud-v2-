import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-foundation-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section aria-labelledby="foundation-title">
      <p class="eyebrow">Sprint 1 · Fundação executável</p>
      <h1 id="foundation-title">Frontend preparado para os fluxos operacionais</h1>
      <p class="summary">
        A base Angular está configurada com routing, environments, HttpClient e
        tratamento centralizado de falhas. As telas de incidentes serão adicionadas
        pelas User Stories aprovadas da Sprint.
      </p>
    </section>
  `,
  styles: `
    section {
      max-width: 48rem;
    }

    .eyebrow {
      margin: 0 0 0.75rem;
      font-size: 0.875rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      font-size: clamp(2rem, 5vw, 3.5rem);
      line-height: 1.05;
      text-wrap: balance;
    }

    .summary {
      margin-block-start: 1.25rem;
      max-width: 65ch;
      font-size: 1.0625rem;
      line-height: 1.6;
    }
  `,
})
export class FoundationPageComponent {}
