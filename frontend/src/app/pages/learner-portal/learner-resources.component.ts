import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-learner-resources',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="resources" aria-labelledby="learner-resources-title">
      <header>
        <p>Resources</p>
        <h1 id="learner-resources-title">Resources and downloads</h1>
        <span>Shared learner resources will appear here when they are ready for student use.</span>
      </header>
      <article>
        <h2>No learner resources yet</h2>
        <p>Your lessons, progress, achievements, and learning paths are still available from Learn.</p>
        <a routerLink="/learn/products">Back to courses</a>
      </article>
    </section>
  `,
  styles: [`
    .resources { color: var(--ee-text); display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, article { background: var(--ee-surface); border: 1px solid var(--ee-border); border-radius: var(--ee-radius-lg, 8px); box-shadow: var(--ee-shadow-soft); padding: clamp(1rem, 3vw, 1.5rem); }
    header p { color: var(--ee-text-muted); font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2 { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1; }
    header span, article p { color: var(--ee-text-soft); }
    article { display: grid; gap: .75rem; }
    a { background: var(--ee-action-primary); border-radius: var(--ee-radius, 6px); color: var(--ee-action-primary-contrast, #fff); font-weight: 900; padding: .65rem .85rem; text-decoration: none; width: fit-content; }
    a:focus-visible { outline: 3px solid var(--ee-focus-ring); outline-offset: 3px; }
  `]
})
export class LearnerResourcesComponent {}
