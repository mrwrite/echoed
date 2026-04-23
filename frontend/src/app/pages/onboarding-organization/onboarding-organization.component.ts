import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { finalize, firstValueFrom } from 'rxjs';
import { OrganizationService } from '../../services/organization.service';
import { MetaService, EnumOption } from '../../services/meta.service';
import { AuthService } from '../../services/auth.service';
import { PermissionsService } from '../../services/permissions.service';
import {
  clearPendingOrganizationSetup,
  readPendingOrganizationSetup,
} from '../../shared/onboarding-flow';

@Component({
  selector: 'app-onboarding-organization',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './onboarding-organization.component.html',
  styleUrl: './onboarding-organization.component.scss',
})
export class OnboardingOrganizationComponent implements OnInit {
  organizationName = '';
  organizationType = '';
  organizationTypes: EnumOption[] = [];
  inferredTypeLabel = '';
  userRole = '';
  isStudentRole = false;
  isSubmitting = false;
  errorMessage = '';

  constructor(
    private organizationService: OrganizationService,
    private metaService: MetaService,
    private authService: AuthService,
    private permissionsService: PermissionsService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    const token = this.authService.getToken();
    const payload = token ? this.authService.getTokenPayload(token) : null;
    this.userRole = payload?.role ?? '';
    this.isStudentRole = this.userRole === 'student';

    const pending = readPendingOrganizationSetup();
    if (pending) {
      this.organizationName = pending.name;
      this.organizationType = pending.type;
    }

    if (!this.organizationType) {
      this.organizationType = this.getOrgTypeForRole(this.userRole);
    }

    this.metaService.getEnums().subscribe({
      next: (enums) => {
        this.organizationTypes = enums.organizationTypes ?? [];
        this.updateTypeLabel();
      },
      error: () => {
        this.updateTypeLabel();
      },
    });
  }

  // Handle submission through Angular ngSubmit + preventDefault to avoid full-page form reloads.
  onSubmit(event?: Event): void {
    event?.preventDefault();

    if (!this.organizationName || !this.organizationType || this.isSubmitting) {
      return;
    }

    this.isSubmitting = true;
    this.errorMessage = '';

    this.organizationService
      .createOrganization({
        name: this.organizationName,
        type: this.organizationType,
      })
      .pipe(finalize(() => (this.isSubmitting = false)))
      .subscribe({
        next: async (org) => {
          const organizations = await firstValueFrom(this.organizationService.refreshOrganizations());
          const createdOrganization = organizations.find((candidate) => candidate.id === org.id) ?? org;
          const activeRole = createdOrganization.role ?? org.role ?? 'org_admin';
          // Set active organization context immediately so menu/permission logic is available after navigation.
          await firstValueFrom(this.organizationService.setActiveOrg(createdOrganization.id, activeRole));
          await this.permissionsService.refreshSession();
          clearPendingOrganizationSetup();

          await this.router.navigateByUrl('/home');
        },
        error: (err) => {
          this.errorMessage = err?.error?.detail || 'Unable to create organization. Please try again.';
        },
      });
  }

  private updateTypeLabel(): void {
    const match = this.organizationTypes.find((t) => t.value === this.organizationType);
    this.inferredTypeLabel = match?.label ?? this.organizationType;
  }

  private getOrgTypeForRole(role: string): string {
    switch (role) {
      case 'parent':
        return 'family';
      case 'teacher':
      case 'instructor':
        return 'school';
      case 'student':
        return 'family';
      default:
        return 'personal';
    }
  }
}
