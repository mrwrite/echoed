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
    permissionsService.permissions$.next(new Set(['role:content_admin', 'nav:workspace', 'nav:products', 'nav:settings']));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).not.toContain('Classes');
  });

  it('renders navigation immediately when ready emits', () => {
    permissionsService.permissions$.next(new Set([
      'role:content_admin',
      'nav:workspace',
      'nav:projects',
      'nav:product-studio',
      'nav:products',
      'nav:knowledge-sources',
      'nav:settings',
    ]));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Studio');
    expect(text).toContain('Projects');
    expect(text).toContain('Content Studio');
    expect(text).toContain('Learning Products');
    expect(text).toContain('Sources');
    expect(text).toContain('Settings');
  });

  it('renders loading state before readiness', () => {
    permissionsService.ready$.next(false);

    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('[aria-label="sidenav-loading"]')).not.toBeNull();
    expect(fixture.nativeElement.querySelector('a')).toBeNull();
  });

  it('keeps compact navigation usable when collapsed', () => {
    component.collapsed = true;
    permissionsService.permissions$.next(new Set(['role:content_admin', 'nav:workspace']));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const firstLink = fixture.nativeElement.querySelector('a') as HTMLAnchorElement;
    const icon = firstLink.querySelector('app-icon');
    const svg = firstLink.querySelector('svg');
    expect(firstLink.getAttribute('aria-label')).toBe('Studio Home');
    expect(firstLink.getAttribute('title')).toBe('Studio Home');
    expect(firstLink.textContent?.trim()).toBe('');
    expect(icon).not.toBeNull();
    expect(svg).not.toBeNull();
    expect(svg?.querySelectorAll('path').length).toBeGreaterThan(0);
  });

  it('keeps important sidebar controls labeled for accessibility', () => {
    permissionsService.permissions$.next(new Set(['role:content_admin', 'nav:workspace']));
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

  it('uses mobile close language when rendered as an overlay', () => {
    component.mobileMode = true;
    permissionsService.permissions$.next(new Set(['role:student']));
    permissionsService.ready$.next(true);

    fixture.detectChanges();

    const toggleButton = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    expect(toggleButton.getAttribute('aria-label')).toBe('Close navigation menu');
  });
});
