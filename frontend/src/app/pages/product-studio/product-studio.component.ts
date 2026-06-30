import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Course } from '../../models/course';
import { Product, Project, Workspace } from '../../models/v2-platform.model';
import { CoursesService } from '../../services/courses.service';
import { V2PlatformService } from '../../services/v2-platform.service';

const PRODUCT_TYPES = [
  'course',
  'learning_path',
  'documentation_pack',
  'onboarding_track',
  'implementation_playbook',
  'knowledge_portal',
  'certification',
  'resource_pack',
];

@Component({
  selector: 'app-product-studio',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <section class="studio" aria-labelledby="product-studio-title">
      <header class="hero">
        <p class="eyebrow">Product Studio</p>
        <h1 id="product-studio-title">Create trusted learning products</h1>
        <p>
          Start with a product shell, connect it to a project, and optionally wrap an existing
          course-backed runtime product. AI generation, analysis, approval, and publishing remain
          future steps.
        </p>
        <div class="hero-actions">
          <a routerLink="/workspace/product-studio/courses/new">Open existing course wizard</a>
          <a routerLink="/workspace/products">View product catalog</a>
        </div>
      </header>

      <div class="metrics" aria-label="Product Studio summary">
        <article><strong>{{ workspaces.length }}</strong><span>Workspaces</span></article>
        <article><strong>{{ projects.length }}</strong><span>Projects</span></article>
        <article><strong>{{ products.length }}</strong><span>Products</span></article>
        <article><strong>{{ courseBackedProductCount }}</strong><span>Course-backed</span></article>
      </div>

      <div class="grid">
        <form class="panel" (ngSubmit)="createProject()" aria-labelledby="new-project-title">
          <div>
            <p class="eyebrow">Step 1</p>
            <h2 id="new-project-title">Create Project Shell</h2>
            <p class="muted">Projects organize sources, artifacts, generation runs, and future product work.</p>
          </div>

          <label>
            Workspace
            <select name="projectWorkspace" [(ngModel)]="projectWorkspaceId" required>
              <option value="" disabled>Select workspace</option>
              <option *ngFor="let workspace of workspaces" [value]="workspace.id">{{ workspace.name }}</option>
            </select>
          </label>

          <label>
            Project name
            <input name="projectName" [(ngModel)]="projectName" required placeholder="Implementation onboarding" />
          </label>

          <label>
            Description
            <textarea name="projectDescription" [(ngModel)]="projectDescription" rows="3" placeholder="What knowledge should this project organize?"></textarea>
          </label>

          <button type="submit" [disabled]="savingProject || !projectWorkspaceId || !projectName">
            {{ savingProject ? 'Creating...' : 'Create Project Shell' }}
          </button>
        </form>

        <form class="panel" (ngSubmit)="createProduct()" aria-labelledby="new-product-title">
          <div>
            <p class="eyebrow">Step 2</p>
            <h2 id="new-product-title">Create Product Shell</h2>
            <p class="muted">This creates only a V2 wrapper. It does not create courses, lessons, units, or activities.</p>
          </div>

          <label>
            Product type
            <select name="productType" [(ngModel)]="productType" required>
              <option *ngFor="let type of productTypes" [value]="type">{{ label(type) }}</option>
            </select>
          </label>

          <label>
            Project
            <select name="productProject" [(ngModel)]="productProjectId">
              <option value="">No project yet</option>
              <option *ngFor="let project of projects" [value]="project.id">{{ project.name }}</option>
            </select>
          </label>

          <label>
            Existing course runtime link
            <select name="courseLink" [(ngModel)]="selectedCourseId" (ngModelChange)="syncCourseTitle()">
              <option value="">No existing course</option>
              <option *ngFor="let course of courses" [value]="course.id">{{ course.title }}</option>
            </select>
          </label>

          <label>
            Product title
            <input name="productTitle" [(ngModel)]="productTitle" required placeholder="API onboarding track" />
          </label>

          <label>
            Description
            <textarea name="productDescription" [(ngModel)]="productDescription" rows="3" placeholder="What should learners or members get from this product?"></textarea>
          </label>

          <div class="checklist" aria-label="Draft setup checklist">
            <p>Draft setup checklist</p>
            <span>Project selected: {{ productProjectId ? 'ready' : 'optional' }}</span>
            <span>Runtime link: {{ selectedCourseId ? 'course-backed' : 'new shell only' }}</span>
            <span>AI generation: not implemented yet</span>
            <span>Governance: existing course/lesson rules remain authoritative</span>
          </div>

          <button type="submit" [disabled]="savingProduct || !productTitle || !workspaceForProduct">
            {{ savingProduct ? 'Creating...' : 'Create Product Shell' }}
          </button>
        </form>
      </div>

      <p class="status" *ngIf="statusMessage" role="status">{{ statusMessage }}</p>

      <section class="panel">
        <div class="list-head">
          <div>
            <p class="eyebrow">Inventory</p>
            <h2>Current products</h2>
          </div>
          <a routerLink="/workspace/products">Open full list</a>
        </div>

        <div class="empty" *ngIf="!products.length">No product shells exist yet.</div>
        <div class="product-list" *ngIf="products.length">
          <article *ngFor="let product of products">
            <div>
              <h3>{{ product.title }}</h3>
              <p>{{ label(product.product_type) }} · {{ product.status }} · {{ product.review_state }}</p>
              <p *ngIf="product.course_id" class="runtime">Links to existing course runtime</p>
            </div>
            <a [routerLink]="['/workspace/products', product.id]">Details</a>
          </article>
        </div>
      </section>
    </section>
  `,
  styles: [`
    .studio { display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); color: #0f172a; }
    .hero, .panel, .metrics article { background: #fff; border: 1px solid rgba(15,23,42,.1); border-radius: 1.5rem; box-shadow: 0 18px 40px rgba(15,23,42,.08); }
    .hero { padding: clamp(1.5rem, 4vw, 3rem); background: radial-gradient(circle at 85% 0%, rgba(14,116,144,.18), transparent 24rem), #fff; }
    .eyebrow { color: #0e7490; font-size: .76rem; font-weight: 900; letter-spacing: .22em; margin: 0 0 .5rem; text-transform: uppercase; }
    h1, h2, h3 { margin: 0; letter-spacing: -.03em; }
    h1 { font-size: clamp(2rem, 5vw, 3.5rem); line-height: .95; }
    .hero p { color: #334155; font-size: 1.05rem; line-height: 1.7; max-width: 74ch; }
    .hero-actions, .list-head { align-items: center; display: flex; flex-wrap: wrap; gap: .75rem; justify-content: space-between; }
    a, button { border-radius: 999px; font-weight: 900; min-height: 2.6rem; padding: .7rem 1rem; text-decoration: none; }
    a { color: #0e7490; }
    .hero-actions a, button { background: #0f172a; color: #fff; border: 0; }
    button:disabled { background: #94a3b8; cursor: not-allowed; }
    .metrics { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr)); }
    .metrics article { padding: 1rem; display: grid; gap: .25rem; }
    .metrics strong { font-size: 2rem; }
    .metrics span, .muted, .product-list p, .empty { color: #475569; }
    .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(min(24rem, 100%), 1fr)); }
    .panel { display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 1.5rem); }
    label { color: #334155; display: grid; font-weight: 800; gap: .4rem; }
    input, select, textarea { border: 1px solid #cbd5e1; border-radius: .9rem; color: #0f172a; padding: .75rem .85rem; width: 100%; }
    input:focus, select:focus, textarea:focus, button:focus-visible, a:focus-visible { outline: 3px solid rgba(14,116,144,.25); outline-offset: 3px; }
    .checklist { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 1rem; display: grid; gap: .35rem; padding: .9rem; }
    .checklist p { font-weight: 900; margin: 0; }
    .status { background: #ecfeff; border-left: 4px solid #0e7490; border-radius: .75rem; color: #164e63; font-weight: 800; padding: .9rem 1rem; }
    .product-list { display: grid; gap: .75rem; }
    .product-list article { align-items: center; border: 1px solid #e2e8f0; border-radius: 1rem; display: flex; gap: 1rem; justify-content: space-between; padding: 1rem; }
    .runtime { color: #0e7490 !important; font-weight: 800; }
  `]
})
export class ProductStudioComponent implements OnInit {
  readonly productTypes = PRODUCT_TYPES;
  workspaces: Workspace[] = [];
  projects: Project[] = [];
  products: Product[] = [];
  courses: Course[] = [];

  projectWorkspaceId = '';
  projectName = '';
  projectDescription = '';
  productType = 'course';
  productProjectId = '';
  selectedCourseId = '';
  productTitle = '';
  productDescription = '';
  savingProject = false;
  savingProduct = false;
  statusMessage = '';

  constructor(
    private readonly v2Platform: V2PlatformService,
    private readonly coursesService: CoursesService,
  ) {}

  ngOnInit(): void {
    this.loadStudio();
  }

  get courseBackedProductCount(): number {
    return this.products.filter(product => !!product.course_id).length;
  }

  get workspaceForProduct(): string {
    const project = this.projects.find(candidate => candidate.id === this.productProjectId);
    return project?.workspace_id || this.projectWorkspaceId || this.workspaces[0]?.id || '';
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }

  syncCourseTitle(): void {
    const course = this.courses.find(candidate => candidate.id === this.selectedCourseId);
    if (course && !this.productTitle) {
      this.productTitle = course.title;
      this.productDescription = course.description;
    }
  }

  createProject(): void {
    if (!this.projectWorkspaceId || !this.projectName) {
      return;
    }
    this.savingProject = true;
    this.v2Platform.createProject({
      workspace_id: this.projectWorkspaceId,
      name: this.projectName,
      description: this.projectDescription || null,
      metadata: { source: 'product_studio_phase_3' },
    }).subscribe({
      next: project => {
        this.statusMessage = `Project shell created: ${project.name}`;
        this.productProjectId = project.id;
        this.projectName = '';
        this.projectDescription = '';
        this.savingProject = false;
        this.loadStudio();
      },
      error: () => {
        this.statusMessage = 'Project shell could not be created.';
        this.savingProject = false;
      }
    });
  }

  createProduct(): void {
    if (!this.productTitle || !this.workspaceForProduct) {
      return;
    }
    this.savingProduct = true;
    this.v2Platform.createProduct({
      workspace_id: this.workspaceForProduct,
      project_id: this.productProjectId || null,
      course_id: this.selectedCourseId || null,
      product_type: this.productType,
      title: this.productTitle,
      description: this.productDescription || null,
      status: 'draft',
      review_state: this.selectedCourseId ? 'runtime_authoritative' : 'not_reviewed',
      access_state: this.selectedCourseId ? 'existing_runtime' : 'private',
      metadata: { source: 'product_studio_phase_3', ai_generation: 'not_implemented' },
    }).subscribe({
      next: product => {
        this.statusMessage = `Product shell ready: ${product.title}`;
        this.productTitle = '';
        this.productDescription = '';
        this.selectedCourseId = '';
        this.savingProduct = false;
        this.loadStudio();
      },
      error: () => {
        this.statusMessage = 'Product shell could not be created.';
        this.savingProduct = false;
      }
    });
  }

  private loadStudio(): void {
    forkJoin({
      workspaces: this.v2Platform.getWorkspaces(),
      projects: this.v2Platform.getProjects(),
      products: this.v2Platform.getProducts(),
      courses: this.coursesService.getCourses(),
    }).subscribe(({ workspaces, projects, products, courses }) => {
      this.workspaces = workspaces;
      this.projects = projects;
      this.products = products;
      this.courses = courses;
      this.projectWorkspaceId ||= workspaces[0]?.id || '';
    });
  }
}
