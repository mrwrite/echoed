import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { AdminAuditEventsComponent } from './admin-audit-events.component';
import { AuditEventsService } from '../../services/audit-events.service';

describe('AdminAuditEventsComponent', () => {
  let fixture: ComponentFixture<AdminAuditEventsComponent>;
  const service = jasmine.createSpyObj('AuditEventsService', ['list', 'export']);
  const event = {
    id: 'event-1', created_at: '2026-08-13T12:00:00Z', schema_version: 1,
    actor_id: 'actor-1', actor_role: 'admin', action: 'platform.role.changed',
    category: 'access', outcome: 'succeeded', target_type: 'user', target_id: 'user-1',
    organization_id: null, request_id: 'request-1', correlation_id: null, reason_code: null,
    before_state: { role: 'student' }, after_state: { role: 'teacher' }, integrity_verified: true,
  };

  beforeEach(async () => {
    service.list.and.returnValue(of({ items: [event], next_cursor: null }));
    service.export.and.returnValue(of(new Blob(['csv'])));
    await TestBed.configureTestingModule({
      imports: [AdminAuditEventsComponent],
      providers: [{ provide: AuditEventsService, useValue: service }],
    }).compileComponents();
    fixture = TestBed.createComponent(AdminAuditEventsComponent);
  });

  it('renders only the minimized event and accessible detail', () => {
    fixture.detectChanges();
    fixture.componentInstance.selected = event;
    fixture.detectChanges();
    const text = fixture.nativeElement.textContent;
    expect(text).toContain('platform role changed');
    expect(text).toContain('State change');
    expect(text).not.toContain('event_hash');
  });

  it('clears stale protected data and announces a load failure', () => {
    fixture.detectChanges();
    service.list.and.returnValue(throwError(() => ({ status: 500, headers: { get: () => 'safe-reference' } })));
    fixture.componentInstance.load();
    fixture.detectChanges();
    expect(fixture.componentInstance.events).toEqual([]);
    expect(fixture.nativeElement.textContent).toContain('Reference: safe-reference');
  });

  it('passes filter state and exposes pagination', () => {
    service.list.and.returnValue(of({ items: [event], next_cursor: 'next' }));
    fixture.componentInstance.action = 'platform.role.changed';
    fixture.componentInstance.load();
    fixture.detectChanges();
    expect(service.list).toHaveBeenCalledWith(jasmine.objectContaining({ action: 'platform.role.changed' }));
    expect(fixture.nativeElement.textContent).toContain('Load more');
  });
});
