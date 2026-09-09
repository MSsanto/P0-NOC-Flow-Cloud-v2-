import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/foundation/foundation-page.component').then(
        (module) => module.FoundationPageComponent,
      ),
    title: 'NOC Flow Cloud v2',
  },
  {
    path: '**',
    redirectTo: '',
  },
];
