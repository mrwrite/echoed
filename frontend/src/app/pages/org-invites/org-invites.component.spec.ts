import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { OrgInvitesComponent } from './org-invites.component';
import { OrganizationService } from '../../services/organization.service';
import { environment } from '../../../environments/environment';

class MockOrgService {
  getActiveOrgId() {
    return 'org-123';
  }
}

describe('OrgInvitesComponent', () => {
  let fixture: ComponentFixture<OrgInvitesComponent>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OrgInvitesComponent, HttpClientTestingModule],
      providers: [{ provide: OrganizationService, useClass: MockOrgService }]
    }).compileComponents();

    fixture = TestBed.createComponent(OrgInvitesComponent);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('renders invite list', () => {
    fixture.detectChanges();

    const req = httpMock.expectOne(`${environment.apiUrl}/api/orgs/org-123/invites`);
    req.flush([]);

    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h2')?.textContent).toContain('Organization invites');

    httpMock.verify();
  });
});
