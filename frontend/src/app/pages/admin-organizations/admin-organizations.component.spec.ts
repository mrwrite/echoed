import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { RouterTestingModule } from '@angular/router/testing';
import { of } from 'rxjs';
import { AdminOrganizationsComponent } from './admin-organizations.component';
import { OrganizationService } from '../../services/organization.service';

describe('AdminOrganizationsComponent', () => {
  let fixture: ComponentFixture<AdminOrganizationsComponent>;
  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [RouterTestingModule, AdminOrganizationsComponent], providers: [
      { provide: OrganizationService, useValue: { refreshOrganizations: () => of([{ id: 'org-1', name: 'Echo Academy', type: 'school', role: 'org_admin' }]) } },
      { provide: ActivatedRoute, useValue: { snapshot: { paramMap: convertToParamMap({}) } } },
    ] }).compileComponents();
    fixture = TestBed.createComponent(AdminOrganizationsComponent); fixture.detectChanges();
  });

  it('labels organization visibility as account-scoped and does not invent member counts', () => {
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('Scoped organization visibility'); expect(text).toContain('Echo Academy'); expect(text).not.toContain('Member count');
  });
});
