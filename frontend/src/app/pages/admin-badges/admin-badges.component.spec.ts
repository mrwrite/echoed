import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { AdminBadgesComponent } from './admin-badges.component';
import { BadgesService } from '../../services/badges.service';
import { PermissionsService } from '../../services/permissions.service';

describe('AdminBadgesComponent', () => {
  let fixture: ComponentFixture<AdminBadgesComponent>;
  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [AdminBadgesComponent], providers: [
      { provide: BadgesService, useValue: { getBadges: () => of([{ id: 'badge-1', title: 'Community Scholar', description: 'Completed the pathway', image_url: '/badge.png', created_at: new Date() }]) } },
      { provide: PermissionsService, useValue: { user$: of({ role: 'admin' }) } },
    ] }).compileComponents();
    fixture = TestBed.createComponent(AdminBadgesComponent); fixture.detectChanges();
  });

  it('provides an accessible badge image name and supported create control', () => {
    const image = fixture.nativeElement.querySelector('img') as HTMLImageElement;
    expect(image.alt).toBe('Community Scholar badge'); expect(fixture.nativeElement.textContent).toContain('Create badge');
  });
});
