import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { V2PlatformService } from '../../services/v2-platform.service';
import { OrganizationCoursesComponent } from './organization-courses.component';

describe('OrganizationCoursesComponent', () => {
  const platform = jasmine.createSpyObj('V2PlatformService', ['getProducts', 'getAccessGrants']);
  let fixture: ComponentFixture<OrganizationCoursesComponent>;

  beforeEach(async () => {
    platform.getProducts.and.returnValue(of([
      { id: 'course', workspace_id: 'w', product_type: 'course', title: 'History', status: 'published', review_state: 'published', access_state: 'available', visibility: 'workspace', pricing_model: 'free', certificate_available: true, featured: false, metadata: {}, created_at: '', updated_at: '' },
      { id: 'resource', workspace_id: 'w', product_type: 'resource_pack', title: 'Source Pack', status: 'published', review_state: 'published', access_state: 'available', visibility: 'workspace', pricing_model: 'free', certificate_available: false, featured: false, metadata: {}, created_at: '', updated_at: '' },
    ]));
    platform.getAccessGrants.and.returnValue(of([{ id: 'g', user_id: 'u', product_id: 'course', workspace_id: 'w', grant_type: 'membership', status: 'active', source: 'membership', metadata: {}, created_at: '', updated_at: '' }]));
    await TestBed.configureTestingModule({ imports: [OrganizationCoursesComponent], providers: [{ provide: V2PlatformService, useValue: platform }] }).compileComponents();
    fixture = TestBed.createComponent(OrganizationCoursesComponent);
  });

  it('shows supported learning offerings and access counts without Studio controls', () => {
    fixture.detectChanges();
    expect(fixture.componentInstance.learningProducts.map(product => product.title)).toEqual(['History']);
    expect(fixture.componentInstance.activeGrantCount('course')).toBe(1);
    expect(fixture.nativeElement.textContent).not.toContain('Edit content');
  });
});
