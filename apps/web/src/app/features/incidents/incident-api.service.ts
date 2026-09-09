import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Incident, IncidentCreateRequest } from './incident.model';

@Injectable({ providedIn: 'root' })
export class IncidentApiService {
  private readonly http = inject(HttpClient);
  private readonly endpoint = `${environment.apiBaseUrl}/incidents`;

  list(): Observable<Incident[]> {
    return this.http.get<Incident[]>(this.endpoint);
  }

  get(id: string): Observable<Incident> {
    return this.http.get<Incident>(`${this.endpoint}/${encodeURIComponent(id)}`);
  }

  create(payload: IncidentCreateRequest): Observable<Incident> {
    return this.http.post<Incident>(this.endpoint, payload);
  }
}
