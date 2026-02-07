import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { UserPreferences } from '../models/user-preferences';

@Injectable({
  providedIn: 'root'
})
export class PreferencesService {
  private apiUrl = `${environment.apiUrl}/api/me/preferences`;
  private preferencesSubject = new BehaviorSubject<UserPreferences | null>(null);

  preferences$ = this.preferencesSubject.asObservable();

  constructor(private http: HttpClient) {}

  loadPreferences(): Observable<UserPreferences> {
    return this.http.get<UserPreferences>(this.apiUrl).pipe(
      tap(prefs => this.preferencesSubject.next(prefs))
    );
  }

  updatePreferences(prefs: UserPreferences): Observable<UserPreferences> {
    return this.http.put<UserPreferences>(this.apiUrl, prefs).pipe(
      tap(updated => this.preferencesSubject.next(updated))
    );
  }
}
