import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { TokenResponse } from '../models/token-response';
import { environment } from '../../environments/environment';
import { RegisterDto } from '../models/register-dto';


@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/api/auth`;
  private authTokenKey = 'auth_token';

  constructor(private http: HttpClient) { }

  login(username: string, password: string): Observable<any> {
    const body = new URLSearchParams();
    body.set('username', username);
    body.set('password', password);

    return this.http.post<TokenResponse>(`${this.apiUrl}/token`, body.toString(), {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    }).pipe (

      tap(response => {
        localStorage.setItem(this.authTokenKey, response.access_token);
      })
    );
  }

  register(user: RegisterDto): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, user );
  }

  logout() {
    localStorage.removeItem(this.authTokenKey);
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  getToken(): string | null{
    return localStorage.getItem(this.authTokenKey);
  }
}
