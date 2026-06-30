import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { GenerationRun } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-generation-run-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="run-detail" aria-labelledby="run-title">
      <a class="back-link" routerLink="/workspace/product-studio/generation-runs">Back to generation runs</a>

      <article *ngIf="generationRun" class="panel">
        <p>Generation Run History</p>
        <h1 id="run-title">{{ generationRun.model_name || 'Generation run' }}</h1>
        <span>{{ generationRun.status }} · {{ generationRun.provider || 'provider pending' }}</span>
        <p class="notice">Phase 4 shows generation metadata only. AI execution is intentionally not implemented here.</p>
      </article>

      <div class="grid" *ngIf="generationRun">
        <article class="panel">
          <h2>Prompt</h2>
          <p>{{ generationRun.prompt || 'No prompt has been recorded yet.' }}</p>
        </article>

        <article class="panel">
          <h2>Output Summary</h2>
          <p>{{ generationRun.output_summary || generationRun.error_message || 'No output has been recorded yet.' }}</p>
        </article>

        <article class="panel">
          <h2>Traceability</h2>
          <dl>
            <dt>Project</dt>
            <dd><a [routerLink]="['/workspace/projects', generationRun.project_id]">{{ generationRun.project_id }}</a></dd>
            <dt>Product</dt>
            <dd>{{ generationRun.product_id || 'Not linked' }}</dd>
            <dt>Started</dt>
            <dd>{{ generationRun.started_at || 'Not started' }}</dd>
            <dt>Completed</dt>
            <dd>{{ generationRun.completed_at || 'Not completed' }}</dd>
          </dl>
        </article>
      </div>
    </section>
  `,
  styles: [`
    .run-detail { color: #0f172a; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    .back-link { color: #0e7490; font-weight: 900; text-decoration: none; width: fit-content; }
    .panel { background: #fff; border: 1px solid rgba(15,23,42,.1); border-radius: 1.4rem; box-shadow: 0 18px 40px rgba(15,23,42,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    article > p:first-child { color: #0e7490; font-size: .76rem; font-weight: 900; letter-spacing: .22em; margin: 0 0 .5rem; text-transform: uppercase; }
    h1, h2 { letter-spacing: -.03em; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); }
    span { color: #0e7490; font-weight: 800; }
    .notice, .panel p, dd { color: #475569; overflow-wrap: anywhere; }
    .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
    dl { display: grid; gap: .4rem; margin: 0; }
    dt { color: #334155; font-weight: 900; }
    dd { margin: 0 0 .75rem; }
    a { color: #0e7490; font-weight: 800; }
    a:focus-visible { outline: 3px solid rgba(14,116,144,.25); outline-offset: 3px; }
  `]
})
export class GenerationRunDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly v2Platform = inject(V2PlatformService);

  generationRun: GenerationRun | null = null;

  ngOnInit(): void {
    const generationRunId = this.route.snapshot.paramMap.get('generationRunId');
    if (!generationRunId) {
      return;
    }
    this.v2Platform.getGenerationRun(generationRunId).subscribe(generationRun => {
      this.generationRun = generationRun;
    });
  }
}
