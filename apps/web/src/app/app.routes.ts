import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'incidents' },
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
  { path: '**', redirectTo: 'incidents' },
];
