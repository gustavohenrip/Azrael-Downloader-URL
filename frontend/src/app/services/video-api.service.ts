import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { timeout } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { DependencyStatus, VideoAnalysis } from '../models/models';

@Injectable({
  providedIn: 'root'
})
export class VideoApiService {

  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  analyze(url: string): Observable<VideoAnalysis> {
    return this.http.post<VideoAnalysis>(`${this.baseUrl}/videos/analyze`, { url }).pipe(
      timeout(30_000)
    );
  }

  getDependencies(): Observable<DependencyStatus> {
    return this.http.get<DependencyStatus>(`${this.baseUrl}/system/dependencies`).pipe(
      timeout(10_000)
    );
  }
}
