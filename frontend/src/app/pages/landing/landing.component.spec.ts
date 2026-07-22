import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LandingComponent } from './landing.component';

describe('LandingComponent', () => {
  it('presents the community mission and usable public actions', async () => {
    await TestBed.configureTestingModule({ imports: [LandingComponent], providers: [provideRouter([])] }).compileComponents();
    const fixture = TestBed.createComponent(LandingComponent);
    fixture.detectChanges();
    const element = fixture.nativeElement as HTMLElement;

    expect(element.querySelectorAll('h1').length).toBe(1);
    expect(element.querySelector('nav')?.getAttribute('aria-label')).toBe('Primary navigation');
    expect(element.textContent).toContain('Culturally grounded learning journeys');
    expect(element.querySelector('a[href="#educators"]')).not.toBeNull();
    expect(element.querySelector('a[href="#developers"]')).not.toBeNull();
    expect(element.querySelector('a[href="/login"]')).not.toBeNull();
  });
});
