import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { finalize } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ApiError } from '../http/api-error';

export type AppRole = 'Admin' | 'Supervisor' | 'Operator' | 'Viewer';
export type AppPermission =
  | 'incident:read'
  | 'incident:create'
  | 'incident:update'
  | 'incident:normalize'
  | 'handover:read'
  | 'handover:finalize';

export interface AuthContext {
  readonly subject: string;
  readonly tenant_id: string;
  readonly roles: readonly AppRole[];
  readonly permissions: readonly AppPermission[];
}

@Injectable({ providedIn: 'root' })
export class AuthContextService {
  private readonly http = inject(HttpClient);

  readonly context = signal<AuthContext | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  readonly authenticated = computed(() => this.context() !== null);

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.http
      .get<AuthContext>(`${environment.apiBaseUrl}/auth/me`)
      .pipe(finalize(() => this.loading.set(false)))
      .subscribe({
        next: (context) => this.context.set(context),
        error: (error: unknown) => {
          this.context.set(null);
          this.error.set(
            error instanceof ApiError
              ? error.message
              : 'Não foi possível carregar o contexto de acesso.',
          );
        },
      });
  }

  can(permission: AppPermission): boolean {
    return this.context()?.permissions.includes(permission) ?? false;
  }
}
