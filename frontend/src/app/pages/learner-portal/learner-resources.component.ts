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
        <span>Downloadable artifacts, documentation packs, and knowledge hub resources are planned for a later phase.</span>
      </header>
      <article>
        <h2>No learner resources yet</h2>
        <p>Course lessons, progress, certificates, and learning paths remain available through the existing governed runtime.</p>
        <a routerLink="/learn/products">Back to products</a>
      </article>
    </section>
  `,
  styles: [`
    .resources { color: #102033; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, article { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p { color: #0f766e; font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2 { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1; }
    header span, article p { color: #526273; }
    article { display: grid; gap: .75rem; }
    a { background: #102033; border-radius: 6px; color: #fff; font-weight: 900; padding: .65rem .85rem; text-decoration: none; width: fit-content; }
    a:focus-visible { outline: 3px solid rgba(15,118,110,.25); outline-offset: 3px; }
  `]
})
export class LearnerResourcesComponent {}
