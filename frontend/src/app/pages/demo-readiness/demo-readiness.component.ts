import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-demo-readiness',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="ee-page" aria-labelledby="demo-readiness-title">
      <header class="ee-page-header">
        <p class="ee-eyebrow">Demo Readiness</p>
        <h1 id="demo-readiness-title" class="ee-page-title">EchoEd explains EchoEd</h1>
        <p class="ee-page-copy">
          A five-minute operator script for showing how EchoEd turns expert knowledge into governed learning
          products without replacing the existing course and lesson runtime.
        </p>
        <div class="ee-action-row">
          <a class="ee-link-button ee-link-button--primary" routerLink="/workspace">Start at Workspace</a>
          <a class="ee-link-button" routerLink="/workspace/product-studio">Product Studio</a>
          <a class="ee-link-button" routerLink="/workspace/review-center">Open Review Center</a>
          <a class="ee-link-button" routerLink="/learn">Learner Portal</a>
        </div>
      </header>

      <section class="pitch-strip" aria-label="EchoEd V2 value proposition">
        <article *ngFor="let callout of callouts">
          <span>{{ callout.kicker }}</span>
          <strong>{{ callout.title }}</strong>
          <p>{{ callout.copy }}</p>
        </article>
      </section>

      <section class="ee-grid ee-grid--wide">
        <article class="ee-panel">
          <div class="ee-panel-header">
            <div>
              <p class="ee-eyebrow">Seed Command</p>
              <h2>Prepare the demo state</h2>
            </div>
            <span class="ee-badge ee-badge--approved">Manual</span>
          </div>
          <p class="ee-muted">
            From the repo root, run the existing deterministic reseed. It restores the governed demo course and
            adds the V2 dogfooding wrapper layer.
          </p>
          <code>backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py</code>
        </article>

        <article class="ee-panel">
          <div class="ee-panel-header">
            <div>
              <p class="ee-eyebrow">Demo Accounts</p>
              <h2>Recommended personas</h2>
            </div>
          </div>
          <ul class="ee-list">
            <li><strong>contentadmin</strong><span>Open Product Studio, projects, artifacts, review, access, and analytics.</span></li>
            <li><strong>normalstudent</strong><span>Open Learner Portal and see product-level access without bypassing lesson governance.</span></li>
            <li><strong>teacher</strong><span>Validate the existing student/course runtime still presents the flagship course.</span></li>
          </ul>
        </article>
      </section>

      <section class="ee-panel">
        <div class="ee-panel-header">
          <div>
            <p class="ee-eyebrow">5-Minute Script</p>
            <h2>Tell the platform story in order</h2>
          </div>
          <span class="ee-badge ee-badge--approved">Pitch ready</span>
        </div>
        <ol class="demo-flow">
          <li *ngFor="let step of steps">
            <span>{{ step.time }}</span>
            <div>
              <strong>{{ step.title }}</strong>
              <em>{{ step.line }}</em>
              <p>{{ step.copy }}</p>
              <a class="ee-link-button" [routerLink]="step.route">{{ step.action }}</a>
            </div>
          </li>
        </ol>
      </section>

      <section class="ee-grid ee-grid--wide">
        <article class="ee-panel">
          <div class="ee-panel-header">
            <div>
              <p class="ee-eyebrow">Guardrails</p>
              <h2>What the demo proves</h2>
            </div>
            <span class="ee-badge">Read-only runtime</span>
          </div>
          <ul class="ee-list">
            <li><strong>Wrapper approval is bounded</strong><span>Approved artifacts and products do not publish lessons.</span></li>
            <li><strong>Access grants are product-level</strong><span>They do not create course enrollments or override lesson readiness.</span></li>
            <li><strong>Analytics are observational</strong><span>Dashboards read wrapper and runtime state without changing progress.</span></li>
            <li><strong>AI is represented, not executed</strong><span>Generation runs and artifacts are seeded as demo metadata only.</span></li>
          </ul>
        </article>

        <article class="ee-panel">
          <div class="ee-panel-header">
            <div>
              <p class="ee-eyebrow">Expected Data</p>
              <h2>Seeded V2 records</h2>
            </div>
          </div>
          <dl class="demo-data">
            <div><dt>Workspace</dt><dd>EchoEd Demo Workspace</dd></div>
            <div><dt>Project</dt><dd>EchoEd V2 Platform Evolution Dogfood</dd></div>
            <div><dt>Products</dt><dd>Operator walkthrough, governance review pack, governed course product</dd></div>
            <div><dt>Artifacts</dt><dd>Approved storyboard, in-review checklist, needs-changes access explainer</dd></div>
            <div><dt>Access</dt><dd>Active manual grant for normalstudent</dd></div>
          </dl>
        </article>
      </section>
    </section>
  `,
  styles: [`
    code { background: #102033; border-radius: 8px; color: #fff; display: block; font-weight: 800; overflow-x: auto; padding: .9rem; }
    .pitch-strip { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); }
    .pitch-strip article { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); display: grid; gap: .35rem; padding: 1rem; }
    .pitch-strip span { color: #0f766e; font-size: .72rem; font-weight: 900; text-transform: uppercase; }
    .pitch-strip strong { color: #102033; }
    .pitch-strip p { color: #526273; margin: 0; }
    .demo-flow { counter-reset: none; display: grid; gap: .85rem; list-style: none; margin: 0; padding: 0; }
    .demo-flow li { border: 1px solid #d8e1ea; border-radius: 8px; display: grid; gap: .85rem; grid-template-columns: 5.5rem 1fr; padding: 1rem; }
    .demo-flow li > span { align-items: center; background: #e7f7f4; border-radius: 999px; color: #0f766e; display: inline-flex; font-weight: 900; height: 2.2rem; justify-content: center; padding: 0 .75rem; width: fit-content; }
    .demo-flow strong { color: #102033; }
    .demo-flow em { color: #0f766e; display: block; font-style: normal; font-weight: 900; margin-top: .15rem; }
    .demo-flow p { color: #526273; margin: .2rem 0 .65rem; }
    .ee-list { display: grid; gap: .7rem; list-style: none; margin: 0; padding: 0; }
    .ee-list li { border-top: 1px solid #edf2f7; display: grid; gap: .2rem; padding-top: .7rem; }
    .ee-list span, .demo-data dd { color: #526273; }
    .demo-data { display: grid; gap: .65rem; margin: 0; }
    .demo-data div { border-top: 1px solid #edf2f7; display: grid; gap: .2rem; padding-top: .65rem; }
    .demo-data dt { color: #334155; font-size: .74rem; font-weight: 900; text-transform: uppercase; }
    .demo-data dd { margin: 0; }
    @media (max-width: 640px) {
      .demo-flow li { grid-template-columns: 1fr; }
    }
  `]
})
export class DemoReadinessComponent {
  readonly callouts = [
    {
      kicker: 'Knowledge In',
      title: 'Projects collect expert source material',
      copy: 'Source wrappers make internal knowledge reusable and traceable before it becomes learning content.',
    },
    {
      kicker: 'AI Understanding',
      title: 'Analysis is visible as pipeline metadata',
      copy: 'The demo shows where AI analysis and generation will sit without running generation execution.',
    },
    {
      kicker: 'Governance',
      title: 'Humans review before delivery',
      copy: 'Artifacts and products move through review while lesson readiness remains authoritative.',
    },
    {
      kicker: 'Delivery',
      title: 'Products package governed runtime access',
      copy: 'Learners see products, but lessons still open only through existing governed course rules.',
    },
    {
      kicker: 'Analytics',
      title: 'Workspace health closes the loop',
      copy: 'Read-only analytics combine wrapper state and runtime engagement for operators.',
    },
  ];

  readonly steps = [
    {
      time: '0:00',
      title: 'Open with the problem',
      line: 'EchoEd is not another LMS; it is a governed product studio for organizational knowledge.',
      copy: 'Start at Workspace and point to the lifecycle: sources, artifacts, products, review, learner access, and analytics in one operating view.',
      route: '/workspace',
      action: 'Open Workspace',
    },
    {
      time: '0:45',
      title: 'Product Studio',
      line: 'Creators start with a product shell, then connect source knowledge and runtime delivery when it is ready.',
      copy: 'Show the product creation sequence and call out that AI generation is a future disabled step, not active execution.',
      route: '/workspace/product-studio',
      action: 'Open Product Studio',
    },
    {
      time: '1:30',
      title: 'Knowledge in',
      line: 'Projects are where source knowledge becomes structured product work.',
      copy: 'Trace the seeded EchoEd project from knowledge sources through generation metadata into reviewable artifacts.',
      route: '/workspace/projects',
      action: 'View Projects',
    },
    {
      time: '2:10',
      title: 'AI understanding to artifacts',
      line: 'Generated outputs are durable artifacts first, not automatically published lessons.',
      copy: 'Show approved, in-review, and needs-changes artifacts as reviewable outputs with source and product relationships.',
      route: '/workspace/artifacts',
      action: 'View Artifacts',
    },
    {
      time: '2:50',
      title: 'Review Center',
      line: 'Trust is the workflow, not a checkbox after the fact.',
      copy: 'Use the Review Center to explain wrapper review, blocked states, and existing lesson governance as the source of truth.',
      route: '/workspace/review-center',
      action: 'Open Review',
    },
    {
      time: '3:35',
      title: 'Product publishing and learner delivery',
      line: 'Products organize access; governed lessons still decide delivery.',
      copy: 'Switch to normalstudent and show product visibility through an access grant without claiming it bypasses runtime readiness.',
      route: '/learn',
      action: 'Open Learner Portal',
    },
    {
      time: '4:25',
      title: 'Analytics',
      line: 'Operators can see product health and pipeline health without adding event tracking yet.',
      copy: 'Close with read-only product, knowledge pipeline, learner engagement, access, and review metrics.',
      route: '/workspace/analytics',
      action: 'Open Analytics',
    },
  ];
}
