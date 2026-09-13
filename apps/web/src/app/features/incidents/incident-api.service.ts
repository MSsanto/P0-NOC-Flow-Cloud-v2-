import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  Incident,
  IncidentCreateRequest,
  IncidentEvent,
  IncidentNormalizeRequest,
  IncidentUpdateRequest,
} from './incident.model';

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

  timeline(id: string): Observable<IncidentEvent[]> {
    return this.http.get<IncidentEvent[]>(
      `${this.endpoint}/${encodeURIComponent(id)}/timeline`,
    );
  }

  addUpdate(id: string, payload: IncidentUpdateRequest): Observable<Incident> {
    return this.http.post<Incident>(
      `${this.endpoint}/${encodeURIComponent(id)}/updates`,
      payload,
    );
  }

  normalize(id: string, payload: IncidentNormalizeRequest): Observable<Incident> {
    return this.http.post<Incident>(
      `${this.endpoint}/${encodeURIComponent(id)}/normalize`,
      payload,
    );
  }
}
