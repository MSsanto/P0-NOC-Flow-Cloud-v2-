import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthContextService } from './core/auth/auth-context.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <a class="skip-link" href="#main-content">Pular para o conteúdo principal</a>

    <div class="app-shell">
      <header class="app-header" role="banner">
        <div>
          <div class="brand">
            <strong>NOC Flow Cloud v2</strong>
            <span class="environment-badge" aria-label="Versão alpha">alpha</span>
          </div>

          <div class="identity" aria-live="polite">
            @if (auth.context(); as context) {
              <span>{{ context.subject }}</span>
              <span class="role-badge">{{ context.roles.join(', ') }}</span>
            } @else if (auth.loading()) {
              <span>Validando acesso…</span>
            } @else if (auth.error()) {
              <span>Contexto de acesso indisponível</span>
            }
          </div>
        </div>
        <nav class="primary-nav" aria-label="Navegação principal">
          <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
          <a routerLink="/incidents" routerLinkActive="active">Incidentes</a>
          @if (auth.can('handover:read')) {
            <a routerLink="/handovers" routerLinkActive="active">Passagem de turno</a>
          }
        </nav>
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

    .app-header > div, .primary-nav {
      max-width: 90rem;
      margin-inline: auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }

    .brand, .identity, .primary-nav {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      min-width: 0;
    }

    .identity {
      justify-content: flex-end;
      font-size: 0.85rem;
      overflow-wrap: anywhere;
    }

    .environment-badge, .role-badge {
      font-size: 0.75rem;
      line-height: 1;
      padding: 0.25rem 0.5rem;
      border: 1px solid currentColor;
      border-radius: 999px;
    }

    .environment-badge {
      text-transform: uppercase;
    }

    .primary-nav {
      margin: .8rem auto 0;
      gap: .35rem;
      flex-wrap: wrap;
    }

    .primary-nav a {
      color: inherit;
      text-decoration: none;
      padding: .45rem .7rem;
      border-radius: .5rem;
      border: 1px solid transparent;
    }

    .primary-nav a:hover, .primary-nav a.active {
      border-color: color-mix(in srgb, CanvasText 24%, transparent);
    }

    .app-main {
      width: min(100% - 2rem, 90rem);
      margin-inline: auto;
      padding-block: clamp(1.5rem, 4vw, 3rem);
      outline: none;
    }

    @media (max-width: 40rem) {
      .app-header > div, .identity {
        align-items: flex-start;
        flex-direction: column;
      }
    }
  `,
})
export class AppComponent implements OnInit {
  readonly auth = inject(AuthContextService);

  ngOnInit(): void {
    this.auth.load();
  }
}
