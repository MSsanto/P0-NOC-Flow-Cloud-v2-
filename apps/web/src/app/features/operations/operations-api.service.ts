import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  DashboardSummary,
  Handover,
  HandoverHistory,
  HandoverPreview,
} from './operations.model';

@Injectable({ providedIn: 'root' })
export class OperationsApiService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiBaseUrl;

  dashboard(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${this.base}/dashboard/summary`);
  }

  preview(): Observable<HandoverPreview> {
    return this.http.get<HandoverPreview>(`${this.base}/handovers/preview`);
  }

  finalize(observations?: string): Observable<Handover> {
    return this.http.post<Handover>(`${this.base}/handovers`, {
      ...(observations ? { observations } : {}),
    });
  }

  latest(): Observable<Handover> {
    return this.http.get<Handover>(`${this.base}/handovers/latest`);
  }

  get(id: string): Observable<Handover> {
    return this.http.get<Handover>(`${this.base}/handovers/${encodeURIComponent(id)}`);
  }

  history(page = 1, pageSize = 25): Observable<HandoverHistory> {
    const params = new HttpParams().set('page', page).set('page_size', pageSize);
    return this.http.get<HandoverHistory>(`${this.base}/handovers`, { params });
  }
}
