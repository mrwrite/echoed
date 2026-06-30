import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import {
  Artifact,
  GenerationRun,
  KnowledgeSource,
  Product,
  Project,
} from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-project-detail',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <section class="project-detail" aria-labelledby="project-title">
      <a class="back-link" routerLink="/workspace/projects">Back to projects</a>

      <header *ngIf="project">
        <p>Knowledge Pipeline</p>
        <h1 id="project-title">{{ project.name }}</h1>
        <span>{{ project.status }} · generation execution is not implemented yet</span>
        <p class="summary">{{ project.description || 'Project shell for source-aware products and artifacts.' }}</p>
      </header>

      <section class="pipeline panel" *ngIf="project" aria-label="Project pipeline map">
        <div><strong>Project</strong><span>{{ project.name }}</span></div>
        <div><strong>Sources</strong><span>{{ knowledgeSources.length }}</span></div>
        <div><strong>Generation Runs</strong><span>{{ generationRuns.length }}</span></div>
        <div><strong>Artifacts</strong><span>{{ artifacts.length }}</span></div>
        <div><strong>Products</strong><span>{{ products.length }}</span></div>
      </section>

      <div class="grid" *ngIf="project">
        <form class="panel" (ngSubmit)="createKnowledgeSource()" aria-labelledby="source-form-title">
          <h2 id="source-form-title">Create knowledge source shell</h2>
          <p>No file upload or parsing runs here. This records a traceable source placeholder for future analysis.</p>
          <label>
            Source title
            <input name="sourceTitle" [(ngModel)]="sourceForm.title" required />
          </label>
          <label>
            Source type
            <select name="sourceType" [(ngModel)]="sourceForm.source_type">
              <option *ngFor="let type of sourceTypes" [value]="type">{{ label(type) }}</option>
            </select>
          </label>
          <label>
            URI or reference
            <input name="sourceUri" [(ngModel)]="sourceForm.uri" placeholder="https://, repo path, or internal note" />
          </label>
          <label>
            Citation
            <textarea name="sourceCitation" [(ngModel)]="sourceForm.citation" rows="3"></textarea>
          </label>
          <button type="submit">Create source shell</button>
        </form>

        <form class="panel" (ngSubmit)="createArtifact()" aria-labelledby="artifact-form-title">
          <h2 id="artifact-form-title">Create artifact shell</h2>
          <p>Artifacts default to draft and review required. They do not publish to learners from this screen.</p>
          <label>
            Artifact title
            <input name="artifactTitle" [(ngModel)]="artifactForm.title" required />
          </label>
          <label>
            Artifact type
            <select name="artifactType" [(ngModel)]="artifactForm.artifact_type">
              <option *ngFor="let type of artifactTypes" [value]="type">{{ label(type) }}</option>
            </select>
          </label>
          <label>
            Related product
            <select name="artifactProduct" [(ngModel)]="artifactForm.product_id">
              <option [ngValue]="null">No product link yet</option>
              <option *ngFor="let product of products" [value]="product.id">{{ product.title }}</option>
            </select>
          </label>
          <label>
            Related source
            <select name="artifactSource" [(ngModel)]="artifactForm.knowledge_source_id">
              <option [ngValue]="null">No source link yet</option>
              <option *ngFor="let source of knowledgeSources" [value]="source.id">{{ source.title }}</option>
            </select>
          </label>
          <label>
            Body
            <textarea name="artifactBody" [(ngModel)]="artifactForm.body" rows="5"></textarea>
          </label>
          <button type="submit">Create draft artifact</button>
        </form>
      </div>

      <p class="message" role="status" *ngIf="message">{{ message }}</p>

      <div class="registry">
        <article class="panel">
          <h2>Products</h2>
          <p *ngIf="!products.length">No products are linked to this project yet.</p>
          <a *ngFor="let product of products" [routerLink]="['/workspace/products', product.id]">
            {{ product.title }} <span>{{ label(product.product_type) }}</span>
          </a>
        </article>

        <article class="panel">
          <h2>Knowledge Sources</h2>
          <p *ngIf="!knowledgeSources.length">No knowledge source shells exist yet.</p>
          <div *ngFor="let source of knowledgeSources" class="record">
            <strong>{{ source.title }}</strong>
            <span>{{ label(source.source_type) }} · {{ source.status }}</span>
            <small>{{ source.citation || source.uri || 'Traceability shell' }}</small>
          </div>
        </article>

        <article class="panel">
          <h2>Artifacts</h2>
          <p *ngIf="!artifacts.length">No draft artifacts exist yet.</p>
          <a *ngFor="let artifact of artifacts" [routerLink]="['/workspace/artifacts', artifact.id]">
            {{ artifact.title }} <span>{{ label(artifact.artifact_type) }} · {{ artifact.review_state }}</span>
          </a>
        </article>

        <article class="panel">
          <h2>Generation Runs</h2>
          <p>Execution is not implemented yet. Future AI runs will appear here with prompt and output metadata.</p>
          <a *ngFor="let run of generationRuns" [routerLink]="['/workspace/product-studio/generation-runs', run.id]">
            {{ run.model_name || 'Generation run' }} <span>{{ run.status }}</span>
          </a>
        </article>
      </div>
    </section>
  `,
  styles: [`
    .project-detail { color: #0f172a; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    .back-link { color: #0e7490; font-weight: 900; text-decoration: none; width: fit-content; }
    header, .panel, .message { background: #fff; border: 1px solid rgba(15,23,42,.1); border-radius: 1.4rem; box-shadow: 0 18px 40px rgba(15,23,42,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p:first-child { color: #0e7490; font-size: .76rem; font-weight: 900; letter-spacing: .22em; margin: 0 0 .5rem; text-transform: uppercase; }
    h1, h2 { letter-spacing: -.03em; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); }
    header span, a span, .record span { color: #0e7490; font-weight: 800; }
    .summary, .panel p, small { color: #475569; }
    .grid, .registry { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
    .pipeline { grid-template-columns: repeat(auto-fit, minmax(8.5rem, 1fr)); }
    .pipeline div { background: #f8fafc; border: 1px solid #d8e1ea; border-radius: 8px; display: grid; gap: .3rem; padding: .85rem; }
    .pipeline strong { color: #102033; }
    .pipeline span { color: #0e7490; font-weight: 900; }
    form { align-content: start; display: grid; gap: .85rem; }
    label { color: #334155; display: grid; font-size: .9rem; font-weight: 800; gap: .35rem; }
    input, select, textarea { border: 1px solid #cbd5e1; border-radius: .8rem; color: #0f172a; font: inherit; padding: .75rem .85rem; }
    input:focus, select:focus, textarea:focus, button:focus-visible, a:focus-visible { outline: 3px solid rgba(14,116,144,.25); outline-offset: 3px; }
    button, .panel a { background: #0f172a; border: 0; border-radius: 999px; color: #fff; cursor: pointer; display: inline-flex; font-weight: 900; justify-content: center; padding: .8rem 1rem; text-decoration: none; }
    .registry .panel { align-content: start; display: grid; gap: .75rem; }
    .record { border-top: 1px solid #e2e8f0; display: grid; gap: .25rem; padding-top: .75rem; }
    @media (max-width: 720px) { .project-detail { padding: 1rem; } }
  `]
})
export class ProjectDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly v2Platform = inject(V2PlatformService);

  project: Project | null = null;
  products: Product[] = [];
  knowledgeSources: KnowledgeSource[] = [];
  artifacts: Artifact[] = [];
  generationRuns: GenerationRun[] = [];
  message = '';

  readonly sourceTypes = ['repository', 'document', 'pdf', 'url', 'transcript', 'upload', 'manual_note'];
  readonly artifactTypes = ['outline', 'documentation', 'guide', 'checklist', 'source_map', 'export_bundle', 'assessment_seed', 'lesson_draft'];

  sourceForm = {
    title: '',
    source_type: 'document',
    uri: '',
    citation: '',
  };

  artifactForm = {
    title: '',
    artifact_type: 'documentation',
    product_id: null as string | null,
    knowledge_source_id: null as string | null,
    body: '',
  };

  ngOnInit(): void {
    this.load();
  }

  createKnowledgeSource(): void {
    if (!this.project || !this.sourceForm.title.trim()) {
      return;
    }

    this.v2Platform.createKnowledgeSource({
      workspace_id: this.project.workspace_id,
      project_id: this.project.id,
      title: this.sourceForm.title.trim(),
      source_type: this.sourceForm.source_type,
      uri: this.sourceForm.uri || null,
      citation: this.sourceForm.citation || null,
      metadata: { created_from: 'project_detail_shell' },
    }).subscribe(source => {
      this.knowledgeSources = [...this.knowledgeSources, source];
      this.sourceForm = { title: '', source_type: 'document', uri: '', citation: '' };
      this.message = 'Knowledge source shell created. No file parsing or AI analysis was run.';
    });
  }

  createArtifact(): void {
    if (!this.project || !this.artifactForm.title.trim()) {
      return;
    }

    this.v2Platform.createArtifact({
      workspace_id: this.project.workspace_id,
      project_id: this.project.id,
      product_id: this.artifactForm.product_id,
      knowledge_source_id: this.artifactForm.knowledge_source_id,
      artifact_type: this.artifactForm.artifact_type,
      title: this.artifactForm.title.trim(),
      body: this.artifactForm.body || null,
      metadata: { created_from: 'manual_artifact_shell' },
    }).subscribe(artifact => {
      this.artifacts = [...this.artifacts, artifact];
      this.artifactForm = {
        title: '',
        artifact_type: 'documentation',
        product_id: null,
        knowledge_source_id: null,
        body: '',
      };
      this.message = 'Draft artifact created. It remains review-required and is not learner-deliverable.';
    });
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  private load(): void {
    const projectId = this.route.snapshot.paramMap.get('projectId');
    if (!projectId) {
      return;
    }

    forkJoin({
      project: this.v2Platform.getProject(projectId),
      products: this.v2Platform.getProducts({ projectId }),
      knowledgeSources: this.v2Platform.getProjectKnowledgeSources(projectId),
      artifacts: this.v2Platform.getProjectArtifacts(projectId),
      generationRuns: this.v2Platform.getProjectGenerationRuns(projectId),
    }).subscribe(result => {
      this.project = result.project;
      this.products = result.products;
      this.knowledgeSources = result.knowledgeSources;
      this.artifacts = result.artifacts;
      this.generationRuns = result.generationRuns;
    });
  }
}
