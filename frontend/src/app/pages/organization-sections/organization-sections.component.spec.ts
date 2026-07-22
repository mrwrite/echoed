import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { provideRouter } from '@angular/router';

import { OrganizationService } from '../../services/organization.service';
import { OrganizationSectionsComponent } from './organization-sections.component';

describe('OrganizationSectionsComponent', () => {
  const organizations = jasmine.createSpyObj('OrganizationService', ['getActiveOrgId', 'getSections']);
  let fixture: ComponentFixture<OrganizationSectionsComponent>;

  beforeEach(async () => {
    organizations.getActiveOrgId.and.returnValue('org-1');
    organizations.getSections.and.returnValue(of([
      { id: 's1', organization_id: 'org-1', course_version_id: 'v1', name: 'History Seminar', mode: 'remote', created_by: 'u1', learner_count: 4 },
      { id: 's2', organization_id: 'org-1', course_version_id: 'v2', name: 'Local Workshop', mode: 'in_person', created_by: 'u2', learner_count: 8 },
    ]));
    await TestBed.configureTestingModule({ imports: [OrganizationSectionsComponent], providers: [{ provide: OrganizationService, useValue: organizations }, provideRouter([])] }).compileComponents();
    fixture = TestBed.createComponent(OrganizationSectionsComponent);
  });

  it('searches and filters scoped class records', () => {
    fixture.detectChanges();
    fixture.componentInstance.modeFilter = 'remote';
    expect(fixture.componentInstance.filteredSections.map(section => section.name)).toEqual(['History Seminar']);
    fixture.componentInstance.searchTerm = 'missing';
    expect(fixture.componentInstance.filteredSections).toEqual([]);
  });
});
