import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AuditEventPage } from './audit.model';

@Injectable({ providedIn: 'root' })
export class AuditApiService {
  private readonly http = inject(HttpClient);

  list(page = 1, pageSize = 25): Observable<AuditEventPage> {
    const params = new HttpParams().set('page', page).set('page_size', pageSize);
    return this.http.get<AuditEventPage>(`${environment.apiBaseUrl}/audit-events`, { params });
  }
}
