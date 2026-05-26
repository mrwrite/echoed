import { RouterTestingModule } from '@angular/router/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';

import { SidebarComponent } from './echo-sidebar.component';
import { PermissionsService } from '../../services/permissions.service';

class MockPermissionsService {
  readonly user$ = new BehaviorSubject<any>({ fullname: 'Test User', role: 'content_admin' });
  readonly permissions$ = new BehaviorSubject<Set<string>>(new Set<string>());
  readonly ready$ = new BehaviorSubject<boolean>(false);
}

describe('SidebarComponent', () => {
  let component: SidebarComponent;
  let fixture: ComponentFixture<SidebarComponent>;
  let permissionsService: MockPermissionsService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RouterTestingModule, SidebarComponent],
      providers: [{ provide: PermissionsService, useClass: MockPermissionsService }]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SidebarComponent);
    component = fixture.componentInstance;
    component.userInfo = { fullname: 'Test User', role: 'content_admin' } as any;
    permissionsService = TestBed.inject(PermissionsService) as unknown as MockPermissionsService;
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('does not render Sections when permissions exclude it', () => {
    permissionsService.permissions$.next(new Set(['nav:dashboard', 'nav:courses', 'nav:preferences']));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).not.toContain('Sections');
  });

  it('renders navigation immediately when ready emits', () => {
    permissionsService.permissions$.next(new Set(['nav:dashboard', 'nav:courses', 'nav:programs', 'nav:certifications', 'nav:preferences']));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Dashboard');
    expect(text).toContain('Courses');
    expect(text).toContain('Programs');
    expect(text).toContain('Certifications');
  });

  it('renders loading state before readiness', () => {
    permissionsService.ready$.next(false);

    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[aria-label="sidenav-loading"]')).not.toBeNull();
    expect(fixture.nativeElement.textContent).not.toContain('Dashboard');
  });

  it('keeps compact navigation usable when collapsed', () => {
    component.collapsed = true;
    permissionsService.permissions$.next(new Set(['nav:dashboard']));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const firstLink = fixture.nativeElement.querySelector('a') as HTMLAnchorElement;
    expect(firstLink.getAttribute('aria-label')).toBe('Dashboard');
    expect(firstLink.getAttribute('title')).toBe('Dashboard');
    expect(firstLink.textContent?.trim()).toBe('');
  });

  it('keeps important sidebar controls labeled for accessibility', () => {
    permissionsService.permissions$.next(new Set(['nav:dashboard']));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const nav = fixture.nativeElement.querySelector('nav') as HTMLElement;
    const toggleButton = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    const shell = fixture.nativeElement.querySelector('aside') as HTMLElement;
    expect(shell.getAttribute('aria-label')).toBe('Sidebar navigation');
    expect(nav.getAttribute('aria-label')).toBe('Primary navigation');
    expect(nav.getAttribute('id')).toBe('echo-primary-navigation');
    expect(toggleButton.getAttribute('aria-label')).toBe('Toggle sidebar');
    expect(toggleButton.getAttribute('aria-expanded')).toBe('true');
    expect(toggleButton.getAttribute('aria-controls')).toBe('echo-primary-navigation');
  });
});
