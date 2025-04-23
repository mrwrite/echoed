import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'echo-login',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule,
    FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private router: Router, private authService: AuthService) { }

  login(event: Event) {
    event.preventDefault();
    this.authService.login(this.username, this.password).subscribe(
      (response) => {
        console.log('Login successful');
        localStorage.setItem('token', response.access_token);
        this.router.navigate(['/home']);
      },
      (error) => {
        console.log('Login failed');
        this.errorMessage = error.errorMessage;
      }
    );
  }
}