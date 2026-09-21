import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/operations/dashboard-page.component').then(
        (module) => module.DashboardPageComponent,
      ),
    title: 'Dashboard · NOC Flow Cloud v2',
  },
  {
    path: 'handovers',
    loadComponent: () =>
      import('./features/operations/handover-page.component').then(
        (module) => module.HandoverPageComponent,
      ),
    title: 'Passagem de turno · NOC Flow Cloud v2',
  },
  {
    path: 'incidents',
    loadComponent: () =>
      import('./features/incidents/incident-list-page.component').then(
        (module) => module.IncidentListPageComponent,
      ),
    title: 'Incidentes · NOC Flow Cloud v2',
  },
  {
    path: 'incidents/new',
    loadComponent: () =>
      import('./features/incidents/incident-create-page.component').then(
        (module) => module.IncidentCreatePageComponent,
      ),
    title: 'Novo incidente · NOC Flow Cloud v2',
  },
  {
    path: 'incidents/:id',
    loadComponent: () =>
      import('./features/incidents/incident-detail-page.component').then(
        (module) => module.IncidentDetailPageComponent,
      ),
    title: 'Detalhe do incidente · NOC Flow Cloud v2',
  },
  { path: '**', redirectTo: 'dashboard' },
];
