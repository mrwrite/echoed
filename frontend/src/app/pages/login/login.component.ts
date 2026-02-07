import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { RoleService } from '../../services/role.service';
import { UserInfo } from '../../models/user-info';

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
  showPassword = false;
  userInfo!: UserInfo;
  userRoles: string[] = [];

  constructor(private router: Router, private authService: AuthService, private roleService: RoleService) { }

  login(event: Event) {
    event.preventDefault();
    this.authService.login(this.username, this.password).subscribe(
      (response) => {
        console.log('Login successful');
        this.userInfo = this.authService.getTokenPayload(response.access_token);
        this.userRoles.push(this.userInfo.role);
        if (response.organizations && response.organizations.length > 0) {
          this.userRoles.push(response.organizations[0].role);
        }
        this.roleService.setUserRoles(this.userRoles);
        this.router.navigate(['/home']);
      },
      (error) => {
        console.log('Login failed');
        this.errorMessage = error?.error?.detail || error?.message || 'Unable to login. Please check your credentials.';
      }
    );
  }
}
