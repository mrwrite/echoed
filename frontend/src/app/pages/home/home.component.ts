import { Component, OnInit } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../components/echo-sidebar/echo-sidebar.component';
import { EchoHeaderComponent } from '../../components/echo-header/echo-header.component';
import { UserDashboardComponent } from "../user-dashboard/user-dashboard.component";
import { UserInfo } from '../../models/user-info';
import { AuthService } from '../../services/auth.service';
import { trigger, style, animate, transition } from '@angular/animations';
import { filter } from 'rxjs/operators';
import { DemoTourService } from '../../services/demo-tour.service';
import { RoleService } from '../../services/role.service';
import { OrganizationService } from '../../services/organization.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, SidebarComponent, EchoHeaderComponent,RouterOutlet],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
  animations: [
    trigger('fade', [
      transition(':enter', [
        style({ opacity: 0 }),
        animate('500ms ease-out', style({ opacity: 1 }))
      ]),
      transition(':leave', [
        animate('500ms ease-in', style({ opacity: 0 }))
      ])
    ])
  ]
})
export class HomeComponent implements OnInit {
  sidebarCollapsed = false;
  userInfo!: UserInfo;
  lessonMode = false;

  constructor(
    private authService: AuthService,
    private router: Router,
    private demoTourService: DemoTourService,
    private roleService: RoleService,
    private organizationService: OrganizationService,
  ) { }

  ngOnInit(): void {
    const access_token = this.authService.getToken();
    if (access_token) {
      this.userInfo = this.authService.getTokenPayload(access_token);
      console.log(this.userInfo);
      if (this.userInfo?.role) {
        const orgRole = this.organizationService.getActiveOrgRole();
        const roles = [this.userInfo.role];
        if (orgRole) {
          roles.push(orgRole);
        }
        this.roleService.setUserRoles(roles);
      }
    }

    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.lessonMode = this.router.url.includes('/lesson/');
      });
  }

  startDemoTour() {
    this.demoTourService.startTour();
  }

}
