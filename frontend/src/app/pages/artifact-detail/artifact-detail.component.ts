import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { Artifact } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-artifact-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <section class="artifact-detail" aria-labelledby="artifact-title">
      <a class="back-link" routerLink="/workspace/artifacts">Back to artifact registry</a>

      <article *ngIf="artifact" class="panel">
        <p>Artifact Registry</p>
        <h1 id="artifact-title">{{ artifact.title }}</h1>
        <div class="badges">
          <span class="ee-badge">{{ label(artifact.artifact_type) }}</span>
          <span class="ee-badge" [ngClass]="badgeClass(artifact.status)">{{ label(artifact.status) }}</span>
          <span class="ee-badge" [ngClass]="badgeClass(artifact.review_state)">{{ label(artifact.review_state) }}</span>
        </div>
        <span>{{ label(artifact.artifact_type) }} · {{ artifact.status }} · {{ artifact.review_state }}</span>
        <p class="notice">This artifact is a reviewable V2 output. It is not learner-deliverable until a future review or publishing flow explicitly attaches it.</p>
      </article>

      <div class="grid" *ngIf="artifact">
        <article class="panel">
          <h2>Content</h2>
          <p class="body">{{ artifact.body || artifact.uri || 'No body or external URI has been added yet.' }}</p>
        </article>

        <article class="panel">
          <h2>Traceability</h2>
          <dl>
            <dt>Project</dt>
            <dd><a [routerLink]="['/workspace/projects', artifact.project_id]">{{ artifact.project_id }}</a></dd>
            <dt>Product</dt>
            <dd>{{ artifact.product_id || 'Not linked' }}</dd>
            <dt>Knowledge source</dt>
            <dd>{{ artifact.knowledge_source_id || 'Not linked' }}</dd>
            <dt>Generation run</dt>
            <dd>{{ artifact.generation_run_id || 'Manual or placeholder artifact' }}</dd>
          </dl>
        </article>
      </div>
    </section>
  `,
  styles: [`
    .artifact-detail { animation: ee-motion-slide-up var(--ee-duration-slow, 260ms) var(--ee-easing-standard, ease) both; color: #0f172a; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    .back-link { color: #0e7490; font-weight: 900; text-decoration: none; width: fit-content; }
    .panel { animation: ee-motion-card-enter var(--ee-duration-slow, 260ms) var(--ee-easing-standard, ease) both; background: #fff; border: 1px solid rgba(15,23,42,.1); border-radius: 1.4rem; box-shadow: 0 18px 40px rgba(15,23,42,.08); padding: clamp(1rem, 3vw, 1.5rem); transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease), border-color var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .grid > .panel:nth-child(2) { animation-delay: 70ms; }
    .panel:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    article > p:first-child { color: #0e7490; font-size: .76rem; font-weight: 900; letter-spacing: .22em; margin: 0 0 .5rem; text-transform: uppercase; }
    h1, h2 { letter-spacing: -.03em; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); }
    span { color: #0e7490; font-weight: 800; }
    .badges { display: flex; flex-wrap: wrap; gap: .5rem; }
    .badges .ee-badge { transition: transform var(--ee-duration-fast, 120ms) var(--ee-easing-standard, ease), border-color var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease), background var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .badges .ee-badge:hover { transform: translateY(-1px); }
    .notice, .body, dd { color: #475569; }
    .grid { display: grid; gap: 1rem; grid-template-columns: minmax(0, 1.4fr) minmax(260px, .8fr); }
    dl { display: grid; gap: .4rem; margin: 0; }
    dt { color: #334155; font-weight: 900; }
    dd { margin: 0 0 .75rem; overflow-wrap: anywhere; }
    a { color: #0e7490; font-weight: 800; }
    a:focus-visible { outline: 3px solid rgba(14,116,144,.25); outline-offset: 3px; }
    @media (max-width: 800px) { .grid { grid-template-columns: 1fr; } }
    @media (prefers-reduced-motion: reduce) { .artifact-detail, .panel { animation: none; } .panel:hover, .badges .ee-badge:hover { transform: none; } }
  `]
})
export class ArtifactDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly v2Platform = inject(V2PlatformService);

  artifact: Artifact | null = null;

  ngOnInit(): void {
    const artifactId = this.route.snapshot.paramMap.get('artifactId');
    if (!artifactId) {
      return;
    }
    this.v2Platform.getArtifact(artifactId).subscribe(artifact => {
      this.artifact = artifact;
    });
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  badgeClass(value: string): string {
    if (['approved', 'published', 'active'].includes(value)) {
      return 'ee-badge--approved';
    }
    if (['rejected', 'blocked', 'revoked'].includes(value)) {
      return 'ee-badge--blocked';
    }
    if (['draft', 'in_review', 'needs_changes'].includes(value)) {
      return 'ee-badge--draft';
    }
    return '';
  }
}
