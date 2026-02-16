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


@Component({
  selector: 'echo-header',
  standalone: true,
  imports: [CommonModule, RouterModule, EchoBreadcrumbsComponent, FormsModule],
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
    this.organizationService.refreshOrganizations().subscribe();
    this.organizationService.organizations$.subscribe(orgs => {
      this.organizations = orgs;
      if (!this.activeOrgId && this.organizations.length > 0) {
        const defaultOrg = this.organizations[0];
        this.switchOrg(defaultOrg.id);
      }
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

  switchOrg(orgId: string) {
    const role = this.organizations.find(org => org.id === orgId)?.role;
    this.organizationService.setActiveOrg(orgId, role).subscribe(async () => {
      this.activeOrgId = orgId;
      this.permissionsService.resetSession();
      await this.permissionsService.bootstrapSession();
    });
  }
}
