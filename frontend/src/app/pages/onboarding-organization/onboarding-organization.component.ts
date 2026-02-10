import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { OrganizationService } from '../../services/organization.service';
import { MetaService, EnumOption } from '../../services/meta.service';
import { AuthService } from '../../services/auth.service';

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
    private router: Router,
  ) {}

  ngOnInit(): void {
    const token = this.authService.getToken();
    const payload = token ? this.authService.getTokenPayload(token) : null;
    this.userRole = payload?.role ?? '';
    this.isStudentRole = this.userRole === 'student';

    const pending = sessionStorage.getItem('pending_org_creation');
    if (pending) {
      try {
        const parsed = JSON.parse(pending);
        this.organizationName = parsed?.name ?? '';
        this.organizationType = parsed?.type ?? '';
      } catch (err) {
        console.warn('Unable to parse pending org creation payload.', err);
      }
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

  createOrganization(): void {
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
      .subscribe({
        next: (org) => {
          sessionStorage.removeItem('pending_org_creation');
          this.organizationService.refreshOrganizations().subscribe();
          this.organizationService.setActiveOrg(org.id, 'org_admin').subscribe({
            next: () => {
              this.isSubmitting = false;
              this.router.navigate(['/home']);
            },
            error: () => {
              this.isSubmitting = false;
              this.router.navigate(['/home']);
            },
          });
        },
        error: (err) => {
          this.isSubmitting = false;
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
