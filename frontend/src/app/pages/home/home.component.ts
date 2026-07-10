import { Component, ElementRef, HostListener, OnDestroy, OnInit, ViewChild, inject } from '@angular/core';
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
export class HomeComponent implements OnInit, OnDestroy {
  sidebarCollapsed = false;
  lessonMode = false;
  compactShell = false;
  mobileNavigationOpen = false;
  @ViewChild('mobileNavTrigger') mobileNavTrigger?: ElementRef<HTMLButtonElement>;
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
        if (this.compactShell) {
          this.closeMobileNavigation();
        }
      });
  }

  ngOnDestroy(): void {
    this.setScrollLock(false);
  }

  @HostListener('window:resize')
  onWindowResize(): void {
    this.syncShellViewport();
  }

  @HostListener('document:keydown.escape')
  onEscapeKey(): void {
    if (this.mobileNavigationOpen) {
      this.closeMobileNavigation(true);
    }
  }

  startDemoTour() {
    this.demoTourService.startTour();
  }

  openMobileNavigation(): void {
    this.mobileNavigationOpen = true;
    this.sidebarCollapsed = false;
    this.setScrollLock(true);
  }

  closeMobileNavigation(restoreFocus = false): void {
    if (!this.mobileNavigationOpen) {
      return;
    }

    this.mobileNavigationOpen = false;
    this.sidebarCollapsed = true;
    this.setScrollLock(false);

    if (restoreFocus) {
      queueMicrotask(() => this.mobileNavTrigger?.nativeElement.focus());
    }
  }

  toggleSidebar(): void {
    if (this.compactShell) {
      if (this.mobileNavigationOpen) {
        this.closeMobileNavigation(true);
      } else {
        this.openMobileNavigation();
      }
      return;
    }

    this.sidebarCollapsed = !this.sidebarCollapsed;
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
    return this.compactShell && this.mobileNavigationOpen;
  }

  private syncShellViewport(): void {
    const nextCompactShell = window.innerWidth < 1024;
    if (nextCompactShell && !this.compactShell) {
      this.sidebarCollapsed = true;
    }

    if (!nextCompactShell && this.mobileNavigationOpen) {
      this.closeMobileNavigation();
      this.sidebarCollapsed = false;
    }

    this.compactShell = nextCompactShell;
  }

  private setScrollLock(locked: boolean): void {
    document.body.classList.toggle('echo-mobile-nav-open', locked);
  }
}
