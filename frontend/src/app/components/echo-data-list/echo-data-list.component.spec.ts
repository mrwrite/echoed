import { TestBed } from '@angular/core/testing';
import { EchoDataListComponent } from './echo-data-list.component';

describe('EchoDataListComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [EchoDataListComponent] }).compileComponents();
  });

  it('renders equivalent desktop rows and mobile records', () => {
    const fixture = TestBed.createComponent(EchoDataListComponent);
    fixture.componentInstance.title = 'Learners';
    fixture.componentInstance.columns = [
      { key: 'name', label: 'Name', primary: true },
      { key: 'status', label: 'Status' },
    ];
    fixture.componentInstance.items = [
      { id: 1, values: { name: 'Ada Lovelace', status: 'Active' } },
      { id: 2, values: { name: 'Mary Jackson', status: 'Invited' } },
    ];
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelectorAll('tbody tr').length).toBe(2);
    expect(fixture.nativeElement.querySelectorAll('[role="listitem"]').length).toBe(2);
    expect(fixture.nativeElement.querySelector('caption').textContent).toContain('Learners');
    expect(fixture.nativeElement.querySelector('[role="status"]').textContent).toContain('2 records');
  });

  it('emits the same named keyboard action for a record', () => {
    const fixture = TestBed.createComponent(EchoDataListComponent);
    fixture.componentInstance.columns = [{ key: 'name', label: 'Name', primary: true }];
    fixture.componentInstance.items = [{ id: 1, values: { name: 'Ada Lovelace' } }];
    fixture.componentInstance.actions = [{ id: 'open', label: 'Open' }];
    spyOn(fixture.componentInstance.actionSelected, 'emit');
    fixture.detectChanges();

    const action = fixture.nativeElement.querySelector('tbody button') as HTMLButtonElement;
    expect(action.getAttribute('aria-label')).toBe('Open Ada Lovelace');
    action.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    action.click();
    expect(fixture.componentInstance.actionSelected.emit).toHaveBeenCalledWith({ actionId: 'open', item: fixture.componentInstance.items[0] });
  });

  it('announces an explanatory empty state', () => {
    const fixture = TestBed.createComponent(EchoDataListComponent);
    fixture.componentInstance.emptyTitle = 'No assignments';
    fixture.componentInstance.emptyMessage = 'Assign learning from a class.';
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('.ee-data-list__empty').textContent).toContain('No assignments');
  });
});
