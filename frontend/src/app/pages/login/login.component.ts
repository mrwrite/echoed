import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { PermissionsService } from '../../services/permissions.service';

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

  constructor(
    private router: Router,
    private authService: AuthService,
    private permissionsService: PermissionsService,
  ) { }

  async login(event: Event) {
    event.preventDefault();

    try {
      await firstValueFrom(this.authService.login(this.username, this.password));
      await this.permissionsService.bootstrapSession();
      const outcome = this.permissionsService.getCurrentOutcome();

      switch (outcome.status) {
        case 'ready':
          await this.router.navigateByUrl('/home');
          return;
        case 'onboardingRequired':
          await this.router.navigateByUrl('/onboarding/organization');
          return;
        case 'failed':
          this.errorMessage = 'Unable to complete session bootstrap. Please try again.';
          return;
        case 'unauthenticated':
          this.errorMessage = 'Your session could not be established. Please log in again.';
          await this.router.navigateByUrl('/login');
          return;
        default:
          this.errorMessage = 'Unable to determine where to continue. Please try again.';
          return;
      }
    } catch (error: any) {
      this.errorMessage = error?.error?.detail || error?.message || 'Unable to login. Please check your credentials.';
    }
  }
}
