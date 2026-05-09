import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EchoStatePanelComponent } from './echo-state-panel.component';

describe('EchoStatePanelComponent', () => {
  let component: EchoStatePanelComponent;
  let fixture: ComponentFixture<EchoStatePanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EchoStatePanelComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EchoStatePanelComponent);
    component = fixture.componentInstance;
    component.variant = 'error';
    component.eyebrow = 'Request failed';
    component.title = 'Unable to load';
    component.body = 'Retry once the connection is stable.';
    component.actionLabel = 'Retry';
    component.ariaLabel = 'Request failure state';
    fixture.detectChanges();
  });

  it('uses alert semantics for error states', () => {
    const panel = fixture.nativeElement.querySelector('[data-echo-state="error"]') as HTMLElement;

    expect(panel.getAttribute('role')).toBe('alert');
    expect(panel.getAttribute('aria-live')).toBe('assertive');
    expect(panel.getAttribute('aria-label')).toBe('Request failure state');
  });

  it('renders retry-capable action content when configured', () => {
    spyOn(component.action, 'emit');
    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;

    expect(button.textContent?.trim()).toBe('Retry');
    button.click();

    expect(component.action.emit).toHaveBeenCalled();
  });

  it('supports responsive centered rendering', () => {
    component.align = 'center';
    fixture.detectChanges();

    const panel = fixture.nativeElement.querySelector('[data-echo-state="error"]') as HTMLElement;
    expect(panel.classList).toContain('echo-state-panel--center');
  });
});
