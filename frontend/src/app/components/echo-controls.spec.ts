import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { EchoButtonComponent } from './echo-button/echo-button.component';
import { EchoCheckboxComponent } from './echo-checkbox/echo-checkbox.component';
import { EchoInputComponent } from './echo-input/echo-input.component';
import { EchoRadioGroupComponent } from './echo-radio-group/echo-radio-group.component';
import { EchoSearchComponent } from './echo-search/echo-search.component';
import { EchoSelectComponent } from './echo-select/echo-select.component';
import { EchoTextareaComponent } from './echo-textarea/echo-textarea.component';
import { EchoToggleComponent } from './echo-toggle/echo-toggle.component';

describe('Echo shared controls', () => {
  it('connects input labels, validation text, and required state', async () => {
    await TestBed.configureTestingModule({ imports: [EchoInputComponent] }).compileComponents();
    const fixture = TestBed.createComponent(EchoInputComponent);
    fixture.componentInstance.label = 'Email address';
    fixture.componentInstance.required = true;
    fixture.componentInstance.error = 'Enter a valid email address.';
    fixture.detectChanges();

    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    const label = fixture.nativeElement.querySelector('label') as HTMLLabelElement;
    expect(label.htmlFor).toBe(input.id);
    expect(input.required).toBeTrue();
    expect(input.getAttribute('aria-invalid')).toBe('true');
    expect(input.getAttribute('aria-describedby')).toContain('-error');
  });

  it('disables and names a loading icon-only button', async () => {
    await TestBed.configureTestingModule({ imports: [EchoButtonComponent] }).compileComponents();
    const fixture = TestBed.createComponent(EchoButtonComponent);
    Object.assign(fixture.componentInstance, { label: 'Save', ariaLabel: 'Save changes', iconOnly: true, icon: '✓', loading: true });
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    expect(button.disabled).toBeTrue();
    expect(button.getAttribute('aria-label')).toBe('Save changes');
    expect(button.getAttribute('aria-busy')).toBe('true');
  });

  it('gives select and textarea controls labels and described validation', async () => {
    await TestBed.configureTestingModule({ imports: [EchoSelectComponent, EchoTextareaComponent] }).compileComponents();
    const selectFixture = TestBed.createComponent(EchoSelectComponent);
    selectFixture.componentInstance.hint = 'Choose one role.';
    selectFixture.detectChanges();
    expect(selectFixture.nativeElement.querySelector('label').htmlFor).toBe(selectFixture.nativeElement.querySelector('select').id);
    expect(selectFixture.nativeElement.querySelector('select').getAttribute('aria-describedby')).toContain('-hint');

    const textareaFixture = TestBed.createComponent(EchoTextareaComponent);
    textareaFixture.componentInstance.error = 'A response is required.';
    textareaFixture.detectChanges();
    expect(textareaFixture.nativeElement.querySelector('textarea').getAttribute('aria-invalid')).toBe('true');
  });

  it('uses native checkbox and radio semantics with described errors', async () => {
    await TestBed.configureTestingModule({ imports: [EchoCheckboxComponent, EchoRadioGroupComponent] }).compileComponents();
    const checkboxFixture = TestBed.createComponent(EchoCheckboxComponent);
    checkboxFixture.componentInstance.error = 'Agreement is required.';
    checkboxFixture.detectChanges();
    expect(checkboxFixture.nativeElement.querySelector('input').getAttribute('aria-describedby')).toContain('-error');

    const radioFixture = TestBed.createComponent(EchoRadioGroupComponent);
    radioFixture.componentInstance.options = [{ label: 'Teacher', value: 'teacher' }, { label: 'Student', value: 'student' }];
    radioFixture.componentInstance.error = 'Choose a role.';
    radioFixture.detectChanges();
    expect(radioFixture.nativeElement.querySelector('fieldset')).not.toBeNull();
    expect(radioFixture.nativeElement.querySelectorAll('input[type="radio"]').length).toBe(2);
  });

  it('exposes a keyboard-operable switch and respects disabled state', async () => {
    await TestBed.configureTestingModule({ imports: [EchoToggleComponent] }).compileComponents();
    const fixture = TestBed.createComponent(EchoToggleComponent);
    fixture.componentInstance.label = 'Email notifications';
    fixture.detectChanges();
    const button = fixture.nativeElement.querySelector('[role="switch"]') as HTMLButtonElement;
    button.click();
    fixture.detectChanges();
    expect(fixture.componentInstance.checked).toBeTrue();
    expect(button.getAttribute('aria-checked')).toBe('true');

    fixture.componentInstance.disabled = true;
    fixture.detectChanges();
    button.click();
    expect(fixture.componentInstance.checked).toBeTrue();
  });

  it('announces search results and provides a named clear action', async () => {
    await TestBed.configureTestingModule({ imports: [EchoSearchComponent] }).compileComponents();
    const fixture: ComponentFixture<EchoSearchComponent> = TestBed.createComponent(EchoSearchComponent);
    fixture.componentInstance.value = 'history';
    fixture.componentInstance.resultCount = 2;
    fixture.detectChanges();

    const clear = fixture.debugElement.query(By.css('.ee-search__clear'));
    expect(clear.attributes['aria-label']).toBe('Clear search');
    clear.triggerEventHandler('click');
    fixture.detectChanges();
    expect(fixture.componentInstance.value).toBe('');
    expect(fixture.nativeElement.querySelector('[role="status"]').textContent).toContain('2 results');
  });
});
