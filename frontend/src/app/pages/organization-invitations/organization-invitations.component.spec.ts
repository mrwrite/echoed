import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { InvitesService } from '../../services/invites.service';
import { OrganizationService } from '../../services/organization.service';
import { OrganizationInvitationsComponent } from './organization-invitations.component';

describe('OrganizationInvitationsComponent', () => {
  let fixture: ComponentFixture<OrganizationInvitationsComponent>;
  const invites = jasmine.createSpyObj('InvitesService', ['listInvites', 'createInvite']);
  const organizations = jasmine.createSpyObj('OrganizationService', ['getActiveOrgId']);

  beforeEach(async () => {
    invites.createInvite.calls.reset();
    invites.listInvites.calls.reset();
    organizations.getActiveOrgId.and.returnValue('org-1');
    invites.listInvites.and.returnValue(of([]));
    await TestBed.configureTestingModule({ imports: [OrganizationInvitationsComponent], providers: [
      { provide: InvitesService, useValue: invites }, { provide: OrganizationService, useValue: organizations },
    ] }).compileComponents();
    fixture = TestBed.createComponent(OrganizationInvitationsComponent);
  });

  it('requires confirmation before creating a privileged invitation', () => {
    fixture.detectChanges();
    const component = fixture.componentInstance;
    component.email = 'leader@example.com';
    component.role = 'org_admin';
    component.requestInvite();
    expect(component.confirmationOpen).toBeTrue();
    expect(invites.createInvite).not.toHaveBeenCalled();
  });

  it('does not expose invitation tokens in visible records', () => {
    invites.listInvites.and.returnValue(of([{ id: 'i1', organization_id: 'org-1', email: 'teacher@example.com', role: 'teacher', token: 'secret-token', expires_at: '2099-01-01', invited_by_user_id: 'u1' }]));
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('teacher@example.com');
    expect(fixture.nativeElement.textContent).not.toContain('secret-token');
  });

  it('preserves form input when invitation creation fails', () => {
    invites.createInvite.and.returnValue(throwError(() => ({ error: { detail: 'Invite failed' } })));
    fixture.detectChanges();
    const component = fixture.componentInstance;
    component.email = 'retry@example.com';
    component.createInvite();
    expect(component.email).toBe('retry@example.com');
    expect(component.formError).toBe('Invite failed');
  });
});
