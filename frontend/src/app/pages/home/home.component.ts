import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../components/echo-sidebar/echo-sidebar.component';
import { EchoHeaderComponent } from '../../components/echo-header/echo-header.component';
import { UserDashboardComponent } from "../user-dashboard/user-dashboard.component";
import { UserInfo } from '../../models/user-info';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, SidebarComponent, EchoHeaderComponent,RouterOutlet],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  sidebarCollapsed = false;
  userInfo!: UserInfo;

  constructor(private authService: AuthService) { }

  ngOnInit(): void {
    var access_token = localStorage.getItem('token');
    if (access_token) {
      this.userInfo = this.authService.getTokenPayload(access_token);      
      console.log(this.userInfo);
    }
  }

}
