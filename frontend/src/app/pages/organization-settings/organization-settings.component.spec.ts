import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, Subject, throwError } from 'rxjs';

import { Organization } from '../../models/organization';
import { OrganizationService } from '../../services/organization.service';
import { OrganizationSettingsComponent } from './organization-settings.component';

describe('OrganizationSettingsComponent', () => {
  let fixture: ComponentFixture<OrganizationSettingsComponent>;
  const organizations = jasmine.createSpyObj('OrganizationService', ['refreshOrganizations', 'getActiveOrgId', 'updateOrganization']);
  const org: Organization = { id: 'org-1', name: 'Original School', type: 'school', role: 'org_admin' };

  beforeEach(async () => {
    organizations.getActiveOrgId.and.returnValue('org-1');
    organizations.refreshOrganizations.and.returnValue(of([org]));
    await TestBed.configureTestingModule({ imports: [OrganizationSettingsComponent], providers: [{ provide: OrganizationService, useValue: organizations }] }).compileComponents();
    fixture = TestBed.createComponent(OrganizationSettingsComponent);
  });

  it('does not update organization presentation before the API confirms success', () => {
    const response = new Subject<Organization>();
    organizations.updateOrganization.and.returnValue(response.asObservable());
    fixture.detectChanges();
    const component = fixture.componentInstance;
    component.nameDraft = 'Renamed School';
    component.save();
    expect(component.organization?.name).toBe('Original School');
    response.next({ ...org, name: 'Renamed School' });
    response.complete();
    expect(component.organization?.name).toBe('Renamed School');
  });

  it('preserves the entered name when save fails', () => {
    organizations.updateOrganization.and.returnValue(throwError(() => ({ error: { detail: 'Save failed' } })));
    fixture.detectChanges();
    fixture.componentInstance.nameDraft = 'Retry School';
    fixture.componentInstance.save();
    expect(fixture.componentInstance.nameDraft).toBe('Retry School');
    expect(fixture.componentInstance.formError).toBe('Save failed');
  });
});
