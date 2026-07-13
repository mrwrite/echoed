import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { User } from '../models/user';



@Injectable({
  providedIn: 'root'
})
export class UsersService {
  private apiUrl = `${environment.apiUrl}/api/users`;
  
  constructor(private http: HttpClient) { }

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}`);
  }

  getUser(userId: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${userId}`);
  }

  updateUserRole(user: User, role: string): Observable<{ message: string }> {
    return this.http.put<{ message: string }>(`${this.apiUrl}/${user.id}`, {
      firstname: user.firstname,
      lastname: user.lastname,
      username: user.username,
      email: user.email,
      password: '',
      role,
    });
  }

  deleteUser(userId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${userId}`);
  }

  getStudents(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/students`);
  }
}
