import { Component, OnDestroy, OnInit } from '@angular/core';
import { SharedUserService } from '../../services/shared-user.service';
import { UserInfo } from '../../models/user-info';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterOutlet } from '@angular/router';
import { PermissionsService } from '../../services/permissions.service';
import { Subscription } from 'rxjs';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';

@Component({
  selector: 'user-dashboard',
  standalone: true,
  imports: [CommonModule, RouterOutlet, EchoLoadingStateComponent],
  templateUrl: './user-dashboard.component.html',
  styleUrl: './user-dashboard.component.scss'
})
export class UserDashboardComponent implements OnInit, OnDestroy {
  userRole: string = 'student'; 
  userInfo: UserInfo | null = null;
  isDashboardView: boolean = true; // Default to true for dashboard view
  isReady = false;
  private readonly subscriptions = new Subscription();

  constructor(private permissionsService: PermissionsService,
      private route: ActivatedRoute,      
      private router: Router,
      private sharedUserService: SharedUserService) { }

      ngOnInit(): void {    
        this.subscriptions.add(this.route.url.subscribe(() => {
          const url = this.router.url;
          this.isDashboardView = !(url.includes('/courses'));
        }));

        this.subscriptions.add(this.permissionsService.ready$.subscribe((ready) => {
          this.isReady = ready;
        }));

        this.subscriptions.add(this.permissionsService.user$.subscribe((userInfo) => {
          this.userInfo = userInfo;
          this.userRole = userInfo?.role ?? 'student';
          if (userInfo) {
            this.sharedUserService.setUserInfo(userInfo);
          }
        }));
      }

      ngOnDestroy(): void {
        this.subscriptions.unsubscribe();
      }
      
  }
