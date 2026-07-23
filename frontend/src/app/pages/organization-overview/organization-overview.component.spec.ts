import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { provideRouter } from '@angular/router';

import { InvitesService } from '../../services/invites.service';
import { OrganizationService } from '../../services/organization.service';
import { V2PlatformService } from '../../services/v2-platform.service';
import { OrganizationOverviewComponent } from './organization-overview.component';

describe('OrganizationOverviewComponent', () => {
  let fixture: ComponentFixture<OrganizationOverviewComponent>;
  const organizations = jasmine.createSpyObj('OrganizationService', ['refreshOrganizations', 'getActiveOrgId', 'getMembers', 'getSections']);
  const invites = jasmine.createSpyObj('InvitesService', ['listInvites']);
  const platform = jasmine.createSpyObj('V2PlatformService', ['getProducts']);

  beforeEach(async () => {
    organizations.getActiveOrgId.and.returnValue('org-1');
    organizations.refreshOrganizations.and.returnValue(of([{ id: 'org-1', name: 'Echo School', type: 'school' }]));
    organizations.getMembers.and.returnValue(of([
      { id: 'm1', user_id: 'u1', display_name: 'T Teacher', username: 'teacher', role: 'teacher', status: 'active', joined_at: '2026-01-01' },
      { id: 'm2', user_id: 'u2', display_name: 'S Student', username: 'student', role: 'student', status: 'active', joined_at: '2026-01-01' },
    ]));
    organizations.getSections.and.returnValue(of([{ id: 's1', organization_id: 'org-1', course_version_id: 'v1', name: 'Class A', mode: 'remote', created_by: 'u1', learner_count: 0 }]));
    invites.listInvites.and.returnValue(of([{ id: 'i1', organization_id: 'org-1', email: 'new@example.com', role: 'teacher', token: 'hidden', expires_at: '2099-01-01', invited_by_user_id: 'u1' }]));
    platform.getProducts.and.returnValue(of([{ id: 'p1', workspace_id: 'w1', product_type: 'course', title: 'Course', status: 'published', review_state: 'published', access_state: 'available', visibility: 'workspace', pricing_model: 'free', certificate_available: false, featured: false, metadata: {}, created_at: '', updated_at: '' }]));
    await TestBed.configureTestingModule({
      imports: [OrganizationOverviewComponent],
      providers: [
        { provide: OrganizationService, useValue: organizations },
        { provide: InvitesService, useValue: invites },
        { provide: V2PlatformService, useValue: platform },
        provideRouter([]),
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(OrganizationOverviewComponent);
  });

  it('shows supported organization counts and attention items', () => {
    fixture.detectChanges();
    const component = fixture.componentInstance;
    expect(component.teachers).toBe(1);
    expect(component.students).toBe(1);
    expect(component.pendingInvites).toBe(1);
    expect(component.emptySections.length).toBe(1);
    expect(fixture.nativeElement.textContent).toContain('Echo School');
  });

  it('preserves available overview data when one summary request fails', () => {
    organizations.getMembers.and.returnValue(throwError(() => new Error('failed')));
    fixture.detectChanges();
    expect(fixture.componentInstance.partialFailures).toContain('member counts');
    expect(fixture.nativeElement.textContent).toContain('Some summary information is unavailable');
  });
});
