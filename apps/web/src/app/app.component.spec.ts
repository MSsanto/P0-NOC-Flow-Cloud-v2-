import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AppComponent } from './app.component';
import { AppPermission, AuthContext, AuthContextService } from './core/auth/auth-context.service';

class AuthContextStub {
  readonly context = signal<AuthContext | null>({
    subject: 'demo-operator@nocflow.local',
    tenant_id: '00000000-0000-4000-8000-000000000001',
    roles: ['Admin'],
    permissions: [
      'incident:read',
      'incident:create',
      'incident:update',
      'incident:normalize',
      'handover:read',
      'handover:finalize',
    ],
  });
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  load(): void {}

  can(permission: AppPermission): boolean {
    return this.context()?.permissions.includes(permission) ?? false;
  }
}

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        provideRouter([]),
        { provide: AuthContextService, useClass: AuthContextStub },
      ],
    }).compileComponents();
  });

  it('renders the product identity, authorized user and main landmark', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();

    const element = fixture.nativeElement as HTMLElement;

    expect(element.querySelector('header')?.textContent).toContain('NOC Flow Cloud v2');
    expect(element.querySelector('header')?.textContent).toContain('demo-operator@nocflow.local');
    expect(element.querySelector('header')?.textContent).toContain('Admin');
    expect(element.querySelector('main#main-content')).not.toBeNull();
    expect(element.querySelector('.skip-link')?.getAttribute('href')).toBe('#main-content');
  });
});
