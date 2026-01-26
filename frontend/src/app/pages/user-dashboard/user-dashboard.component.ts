import { Component, Input, OnInit } from '@angular/core';
import { AuthService } from '../../services/auth.service'
import { SharedUserService } from '../../services/shared-user.service';
import { UserInfo } from '../../models/user-info';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterOutlet } from '@angular/router';

@Component({
  selector: 'user-dashboard',
  standalone: true,
  imports: [CommonModule, RouterOutlet],
  templateUrl: './user-dashboard.component.html',
  styleUrl: './user-dashboard.component.scss'
})
export class UserDashboardComponent implements OnInit {
  userRole: string = 'student'; 
  userInfo!: UserInfo;
  isDashboardView: boolean = true; // Default to true for dashboard view

  constructor(private authService: AuthService, 
      private route: ActivatedRoute,      
      private router: Router,
      private sharedUserService: SharedUserService) { }

      ngOnInit(): void {    
        this.route.url.subscribe(urlSegments => {
          const url = this.router.url;
          this.isDashboardView = !(url.includes('/courses'));
        });
      
        const access_token = this.authService.getToken();
        if (access_token) {
          this.userInfo = this.authService.getTokenPayload(access_token);      
          if (this.userInfo) {
            this.sharedUserService.setUserInfo(this.userInfo);
          } else {
            // ❗ Invalid token - redirect to login
            this.router.navigate(['/login']);
          }
        } else {
          // ❗ No token found - redirect to login
          this.router.navigate(['/login']);
        }
      }
      
  }
