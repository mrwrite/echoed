import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActivatedRoute } from '@angular/router';
import { of, throwError } from 'rxjs';

import { OrganizationService } from '../../services/organization.service';
import { OrganizationPeopleComponent } from './organization-people.component';

describe('OrganizationPeopleComponent', () => {
  let fixture: ComponentFixture<OrganizationPeopleComponent>;
  const organizations = jasmine.createSpyObj('OrganizationService', ['getActiveOrgId', 'getMembers']);

  beforeEach(async () => {
    organizations.getActiveOrgId.and.returnValue('org-1');
    organizations.getMembers.and.returnValue(of([
      { id: '1', user_id: 'u1', display_name: 'Ada Teacher', username: 'ada', role: 'teacher', status: 'active', joined_at: '2026-01-01' },
      { id: '2', user_id: 'u2', display_name: 'Sam Student', username: 'sam', role: 'student', status: 'active', joined_at: '2026-01-01' },
    ]));
    await TestBed.configureTestingModule({
      imports: [OrganizationPeopleComponent],
      providers: [
        { provide: OrganizationService, useValue: organizations },
        { provide: ActivatedRoute, useValue: { snapshot: { data: { mode: 'teachers' } } } },
      ],
    }).compileComponents();
    fixture = TestBed.createComponent(OrganizationPeopleComponent);
  });

  it('limits teacher view to organization teacher roles and supports search', () => {
    fixture.detectChanges();
    expect(fixture.componentInstance.filteredMembers.map(member => member.display_name)).toEqual(['Ada Teacher']);
    fixture.componentInstance.searchTerm = 'missing';
    expect(fixture.componentInstance.filteredMembers).toEqual([]);
  });

  it('shows a safe load error without retaining membership data', () => {
    organizations.getMembers.and.returnValue(throwError(() => new Error('failed')));
    fixture.detectChanges();
    expect(fixture.componentInstance.members).toEqual([]);
    expect(fixture.componentInstance.loadError).toContain('No membership data was changed');
  });
});
