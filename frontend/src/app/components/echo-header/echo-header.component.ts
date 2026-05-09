import { 
  Component, 
  Input, 
  ElementRef, 
  HostListener, 
  ViewChild,
  OnInit
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserInfo } from '../../models/user-info';
import {
  trigger,
  style,
  transition,
  animate
} from '@angular/animations';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';
import { DemoTourService } from '../../services/demo-tour.service';
import { EchoBreadcrumbsComponent } from '../echo-breadcrumbs/echo-breadcrumbs.component';
import { OrganizationService } from '../../services/organization.service';
import { Organization } from '../../models/organization';
import { PermissionsService } from '../../services/permissions.service';
import { EchoStatePanelComponent } from '../echo-state-panel/echo-state-panel.component';
import { EchoLoadingStateComponent } from '../echo-loading-state/echo-loading-state.component';


@Component({
  selector: 'echo-header',
  standalone: true,
  imports: [CommonModule, RouterModule, EchoBreadcrumbsComponent, FormsModule, EchoStatePanelComponent, EchoLoadingStateComponent],
  templateUrl: './echo-header.component.html',
  styleUrl: './echo-header.component.scss',
  animations: [
    trigger('menuAnim', [
      transition(':enter', [
        style({ opacity: 0, transform: 'scale(0.95)' }),
        animate('150ms ease-out', style({ opacity: 1, transform: 'scale(1)' })),
      ]),
      transition(':leave', [
        animate('100ms ease-in', style({ opacity: 0, transform: 'scale(0.95)' })),
      ]),
    ]),
  ],
})

export class EchoHeaderComponent implements OnInit {
  @Input() userinfo!: UserInfo;
  menuOpen: boolean = false;
  organizations: Organization[] = [];
  activeOrgId: string | null = null;
  orgsLoading = true;
  orgsLoadError = '';
  switchPending = false;
  switchError = '';
  switchSuccess = '';

  @ViewChild('menuContainer') menuContainer!: ElementRef;

  constructor(
    private authService: AuthService,
    private router: Router,
    private demoTourService: DemoTourService,
    private organizationService: OrganizationService,
    private permissionsService: PermissionsService
  ) {}

  ngOnInit(): void {
    this.activeOrgId = this.organizationService.getActiveOrgId();
    this.refreshOrganizations();
    this.organizationService.activeOrg$.subscribe((activeOrgId) => {
      this.activeOrgId = activeOrgId;
    });
    this.organizationService.organizations$.subscribe(orgs => {
      this.organizations = orgs;
    });
  }

  getInitials(): string {
    return this.userinfo?.fullname
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase();
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }

  get activeOrganizationName(): string {
    return this.organizations.find((org) => org.id === this.activeOrgId)?.name || 'No confirmed organization';
  }

  logout(): void {
    this.authService.logout();
    this.organizationService.clearActiveOrg();
    this.permissionsService.resetSession();
    this.router.navigate(['/login']);
  }

  startGuidedTour() {
    this.demoTourService.startTour();
  }

  @HostListener('document:click', ['$event.target'])
  onClickOutside(targetElement: HTMLElement) {
    if (this.menuContainer && !this.menuContainer.nativeElement.contains(targetElement)) {
      this.menuOpen = false;
    }
  }

  refreshOrganizations(): void {
    this.orgsLoading = true;
    this.orgsLoadError = '';
    this.organizationService.refreshOrganizations().subscribe({
      next: () => {
        this.orgsLoading = false;
      },
      error: () => {
        this.orgsLoading = false;
        this.orgsLoadError = 'We could not load organizations right now. Retry to restore your confirmed access context.';
      },
    });
  }

  switchOrg(orgId: string) {
    if (!orgId || orgId === this.activeOrgId || this.switchPending) {
      return;
    }

    this.switchPending = true;
    this.switchError = '';
    this.switchSuccess = '';
    this.organizationService.setActiveOrg(orgId).subscribe({
      next: async () => {
        this.activeOrgId = this.organizationService.getActiveOrgId();
        this.permissionsService.resetSession();
        await this.permissionsService.bootstrapSession();
        this.switchPending = false;
        this.switchSuccess = this.activeOrganizationName === 'No confirmed organization'
          ? 'Organization context updated.'
          : `Confirmed organization: ${this.activeOrganizationName}.`;
      },
      error: () => {
        // Preserve the prior confirmed org state when switch confirmation fails.
        this.switchPending = false;
        this.switchError = 'We could not switch organizations. Your confirmed organization context has not changed.';
      },
    });
  }
}
