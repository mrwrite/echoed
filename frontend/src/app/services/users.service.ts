import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { AuthService } from './auth.service';
import { tap } from 'rxjs/operators';
import { TokenResponse } from '../models/token-response';
import { environment } from '../../environments/environment';
import { User } from '../models/user';



@Injectable({
  providedIn: 'root'
})
export class UsersService {
  private apiUrl = `${environment.apiUrl}/api/users`;
  
  constructor(private http: HttpClient, private authService: AuthService) { }

  private getHeaders(): HttpHeaders {
    let token = this.authService.getToken();
    if (token && !token.startsWith('Bearer ')) {
      token = `Bearer ${token}`;
    } else if (!token) {
      token = `Bearer ${this.authService.getToken()}`;
    }
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: token || '' }); 
      
  }

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}`, { headers: this.getHeaders() });
  }
}
