import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { firstValueFrom } from 'rxjs';
import { AuthService } from '../services/auth.service';
import { PermissionsService } from '../services/permissions.service';

@Injectable({
  providedIn: 'root'
})
export class HomeSessionGuard implements CanActivate {
  constructor(
    private authService: AuthService,
    private permissionsService: PermissionsService,
    private router: Router,
  ) {}

  async canActivate(): Promise<boolean> {
    if (!this.authService.getToken()) {
      await this.router.navigate(['/login']);
      return false;
    }

    await this.permissionsService.bootstrapSession();
    const ready = await firstValueFrom(this.permissionsService.ready$);
    if (!ready) {
      await this.router.navigate(['/login']);
      return false;
    }

    return true;
  }
}
