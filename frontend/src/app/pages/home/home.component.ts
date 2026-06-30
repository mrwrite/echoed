import { Component, HostListener, OnInit, inject } from '@angular/core';
import { RouterOutlet, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { SidebarComponent } from '../../components/echo-sidebar/echo-sidebar.component';
import { EchoHeaderComponent } from '../../components/echo-header/echo-header.component';
import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { trigger, style, animate, transition } from '@angular/animations';
import { filter } from 'rxjs/operators';
import { DemoTourService } from '../../services/demo-tour.service';
import { PermissionsService } from '../../services/permissions.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, SidebarComponent, EchoHeaderComponent, EchoLoadingStateComponent, RouterOutlet],
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
  compactShell = false;
  private readonly permissionsService = inject(PermissionsService);
  readonly userInfo$ = this.permissionsService.user$;
  readonly ready$ = this.permissionsService.ready$;

  constructor(
    private router: Router,
    private demoTourService: DemoTourService,
  ) { }

  ngOnInit(): void {
    this.syncShellViewport();
    this.lessonMode = this.router.url.includes('/lesson/');
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.lessonMode = this.router.url.includes('/lesson/');
      });
  }

  @HostListener('window:resize')
  onWindowResize(): void {
    this.syncShellViewport();
  }

  startDemoTour() {
    this.demoTourService.startTour();
  }

  get sidebarWidth(): string {
    if (this.compactShell && !this.sidebarCollapsed) {
      return 'var(--echo-sidebar-collapsed-width)';
    }

    return this.sidebarCollapsed
      ? 'var(--echo-sidebar-collapsed-width)'
      : 'var(--echo-sidebar-expanded-width)';
  }

  get sidebarOverlayMode(): boolean {
    return this.compactShell && !this.sidebarCollapsed;
  }

  private syncShellViewport(): void {
    const nextCompactShell = window.innerWidth < 1024;
    if (nextCompactShell && !this.compactShell) {
      this.sidebarCollapsed = true;
    }

    this.compactShell = nextCompactShell;
  }
}
