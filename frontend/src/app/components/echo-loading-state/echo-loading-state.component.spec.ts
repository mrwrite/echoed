import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EchoLoadingStateComponent } from './echo-loading-state.component';

describe('EchoLoadingStateComponent', () => {
  let component: EchoLoadingStateComponent;
  let fixture: ComponentFixture<EchoLoadingStateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EchoLoadingStateComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EchoLoadingStateComponent);
    component = fixture.componentInstance;
    component.title = 'Loading shell';
    component.body = 'Preparing the authenticated experience.';
    component.ariaLabel = 'shell-loading';
    fixture.detectChanges();
  });

  it('uses status semantics for loading states', () => {
    const panel = fixture.nativeElement.querySelector('[data-echo-loading]') as HTMLElement;

    expect(panel.getAttribute('role')).toBe('status');
    expect(panel.getAttribute('aria-live')).toBe('polite');
    expect(panel.getAttribute('aria-label')).toBe('shell-loading');
  });

  it('supports responsive density variants', () => {
    component.density = 'compact';
    fixture.detectChanges();

    const panel = fixture.nativeElement.querySelector('[data-echo-loading="compact"]') as HTMLElement;
    expect(panel.classList).toContain('echo-loading-state--compact');
  });
});
