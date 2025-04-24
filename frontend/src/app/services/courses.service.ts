import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';
import { Course } from '../models/course';

@Injectable({
  providedIn: 'root'
})
export class CoursesService {
  private apiUrl = `${environment.apiUrl}/api/courses`;

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
      Authorization: token || ''
    });
  }

  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.apiUrl}`, { headers: this.getHeaders() });
  }
}
