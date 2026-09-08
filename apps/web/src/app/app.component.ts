import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <a class="skip-link" href="#main-content">Pular para o conteúdo principal</a>

    <div class="app-shell">
      <header class="app-header" role="banner">
        <div>
          <strong>NOC Flow Cloud v2</strong>
          <span class="environment-badge" aria-label="Versão alpha">alpha</span>
        </div>
      </header>

      <main id="main-content" class="app-main" tabindex="-1">
        <router-outlet />
      </main>
    </div>
  `,
  styles: `
    :host {
      display: block;
      min-height: 100dvh;
    }

    .skip-link {
      position: fixed;
      z-index: 1000;
      inset-block-start: 0.5rem;
      inset-inline-start: 0.5rem;
      padding: 0.75rem 1rem;
      transform: translateY(-200%);
      background: Canvas;
      color: CanvasText;
      border: 2px solid currentColor;
      border-radius: 0.375rem;
    }

    .skip-link:focus {
      transform: translateY(0);
    }

    .app-shell {
      min-height: 100dvh;
      display: grid;
      grid-template-rows: auto 1fr;
    }

    .app-header {
      padding: 1rem clamp(1rem, 4vw, 2rem);
      border-block-end: 1px solid color-mix(in srgb, CanvasText 18%, transparent);
    }

    .app-header > div {
      max-width: 90rem;
      margin-inline: auto;
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .environment-badge {
      font-size: 0.75rem;
      line-height: 1;
      padding: 0.25rem 0.5rem;
      border: 1px solid currentColor;
      border-radius: 999px;
      text-transform: uppercase;
    }

    .app-main {
      width: min(100% - 2rem, 90rem);
      margin-inline: auto;
      padding-block: clamp(1.5rem, 4vw, 3rem);
      outline: none;
    }
  `,
})
export class AppComponent {}
