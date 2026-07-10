import { SimpleChange } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EchoConfirmationDialogComponent } from './echo-confirmation-dialog.component';

describe('EchoConfirmationDialogComponent', () => {
  let component: EchoConfirmationDialogComponent;
  let fixture: ComponentFixture<EchoConfirmationDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EchoConfirmationDialogComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EchoConfirmationDialogComponent);
    component = fixture.componentInstance;
    component.open = true;
    component.title = 'Delete course';
    component.description = 'This removes the course from learners who can access it.';
    component.objectName = 'Introduction to Africa';
    component.confirmLabel = 'Delete course';
    component.variant = 'danger';
    fixture.detectChanges();
  });

  it('renders destructive confirmation copy with dialog semantics', () => {
    const dialog = fixture.nativeElement.querySelector('[role="dialog"]') as HTMLElement;

    expect(dialog.getAttribute('aria-modal')).toBe('true');
    expect(fixture.nativeElement.textContent).toContain('Destructive action');
    expect(fixture.nativeElement.textContent).toContain('Introduction to Africa');
    expect(fixture.nativeElement.textContent).toContain('Delete course');
  });

  it('places initial focus on the safe cancel action', () => {
    const cancelButton = fixture.nativeElement.querySelector('.echo-dialog__button--secondary') as HTMLButtonElement;

    expect(document.activeElement).toBe(cancelButton);
  });

  it('emits cancel on Escape when not loading', () => {
    spyOn(component.cancel, 'emit');

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));

    expect(component.cancel.emit).toHaveBeenCalled();
  });

  it('does not close on Escape while loading', () => {
    spyOn(component.cancel, 'emit');
    component.loading = true;
    fixture.detectChanges();

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));

    expect(component.cancel.emit).not.toHaveBeenCalled();
  });

  it('traps Tab focus inside the dialog', () => {
    const buttons = fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>;
    const cancelButton = buttons[0];
    const confirmButton = buttons[1];
    confirmButton.focus();

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab' }));

    expect(document.activeElement).toBe(cancelButton);
  });

  it('restores focus to the trigger after close', () => {
    const trigger = document.createElement('button');
    document.body.appendChild(trigger);
    trigger.focus();

    component.open = false;
    (component as any).previouslyFocused = trigger;
    component.ngOnChanges({
      open: new SimpleChange(true, false, false),
    });

    expect(document.activeElement).toBe(trigger);
    trigger.remove();
  });
});
