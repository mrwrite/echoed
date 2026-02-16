import { Component, OnInit, inject } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../components/echo-sidebar/echo-sidebar.component';
import { EchoHeaderComponent } from '../../components/echo-header/echo-header.component';
import { trigger, style, animate, transition } from '@angular/animations';
import { filter } from 'rxjs/operators';
import { DemoTourService } from '../../services/demo-tour.service';
import { PermissionsService } from '../../services/permissions.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, SidebarComponent, EchoHeaderComponent, RouterOutlet],
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
  lessonMode = false;
  private readonly permissionsService = inject(PermissionsService);
  readonly userInfo$ = this.permissionsService.user$;

  constructor(
    private router: Router,
    private demoTourService: DemoTourService,
  ) { }

  ngOnInit(): void {
    void this.permissionsService.bootstrapSession();

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
