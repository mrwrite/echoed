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
          Product Studio is the flagship workflow: bring knowledge in, prepare AI understanding,
          generate reviewable artifacts later, govern every decision, then package approved work as
          products that reuse the existing learner runtime.
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

      <section class="workflow panel" aria-labelledby="studio-workflow-title">
        <div class="list-head">
          <div>
            <p class="eyebrow">Flagship workflow</p>
            <h2 id="studio-workflow-title">Create Product to Governed Publish</h2>
          </div>
          <span class="future-pill">AI execution not implemented</span>
        </div>
        <ol>
          <li><strong>Create Product</strong><span>Define the wrapper and intended product type.</span></li>
          <li><strong>Choose Product Type</strong><span>Course, path, resource pack, or documentation package.</span></li>
          <li><strong>Connect Project</strong><span>Attach sources, artifacts, and product work to a project.</span></li>
          <li><strong>Add Knowledge Sources</strong><span>Record traceable source shells for future analysis.</span></li>
          <li class="disabled"><strong>Generate Artifacts</strong><span>Coming soon. No AI generation runs from this phase.</span></li>
          <li><strong>Review</strong><span>Use Review Center for wrapper status and lesson readiness context.</span></li>
          <li class="disabled"><strong>Publish</strong><span>Wrapper approval does not override runtime governance.</span></li>
        </ol>
      </section>

      <section class="panel pitch-cards" aria-label="Product Studio pitch callouts">
        <article><span>Knowledge In</span><strong>Connect project sources</strong><p>Product work starts from traceable workspace knowledge.</p></article>
        <article><span>AI Understanding</span><strong>Prepare analysis safely</strong><p>Generation remains marked as future work in this phase.</p></article>
        <article><span>Review</span><strong>Govern artifacts and products</strong><p>Review status is additive and does not publish lessons.</p></article>
        <article><span>Publish</span><strong>Wrap existing runtime</strong><p>Course-backed products reuse current Course, Unit, Lesson, and readiness rules.</p></article>
      </section>

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
            Subtitle
            <input name="productSubtitle" [(ngModel)]="productSubtitle" placeholder="Turn internal expertise into governed onboarding" />
          </label>

          <label>
            Pricing model
            <select name="pricingModel" [(ngModel)]="pricingModel">
              <option value="internal">Internal</option>
              <option value="free">Free</option>
              <option value="paid">Paid placeholder</option>
              <option value="enterprise">Enterprise placeholder</option>
            </select>
          </label>

          <label>
            Visibility
            <select name="visibility" [(ngModel)]="visibility">
              <option value="draft">Draft</option>
              <option value="private">Private</option>
              <option value="workspace">Workspace</option>
              <option value="invite_only">Invite only</option>
              <option value="public">Public placeholder</option>
            </select>
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
    .studio { display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); color: var(--ee-text); }
    .hero, .panel, .metrics article { background: linear-gradient(145deg, rgba(255,255,255,.1), rgba(255,255,255,.035)), var(--ee-surface); border: 1px solid var(--ee-border); border-radius: var(--ee-radius); box-shadow: var(--ee-shadow-soft); backdrop-filter: blur(22px) saturate(1.2); }
    .hero { padding: clamp(1.75rem, 5vw, 4rem); background: radial-gradient(circle at 85% 0%, rgba(92,200,255,.2), transparent 24rem), radial-gradient(circle at 12% 14%, rgba(167,139,250,.28), transparent 18rem), var(--ee-surface); }
    .eyebrow { color: var(--ee-gold); font-size: .76rem; font-weight: 900; letter-spacing: .22em; margin: 0 0 .5rem; text-transform: uppercase; }
    h1, h2, h3 { color: var(--ee-text); margin: 0; letter-spacing: 0; }
    h1 { font-size: clamp(2.65rem, 7vw, 5.5rem); line-height: .92; max-width: 12ch; }
    .hero p { color: var(--ee-text-soft); font-size: 1.05rem; line-height: 1.7; max-width: 74ch; }
    .hero-actions, .list-head { align-items: center; display: flex; flex-wrap: wrap; gap: .75rem; justify-content: space-between; }
    a, button { border-radius: 999px; font-weight: 900; min-height: 2.6rem; padding: .7rem 1rem; text-decoration: none; }
    a { color: var(--ee-azure); }
    .hero-actions a, button { background: linear-gradient(135deg, var(--ee-purple-strong), var(--ee-purple), var(--ee-azure)); color: #fff; border: 1px solid rgba(255,255,255,.18); box-shadow: 0 16px 34px rgba(92,200,255,.16); }
    button:disabled { background: rgba(255,255,255,.1); color: var(--ee-text-muted); cursor: not-allowed; }
    .metrics { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fit, minmax(9rem, 1fr)); }
    .metrics article { padding: 1rem; display: grid; gap: .25rem; }
    .metrics strong { color: var(--ee-text); font-size: 2rem; }
    .metrics span, .muted, .product-list p, .empty { color: var(--ee-text-soft); }
    .workflow ol { display: grid; gap: .7rem; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); list-style: none; margin: 0; padding: 0; }
    .workflow li { animation: ee-motion-card-enter var(--ee-duration-slow, 260ms) var(--ee-easing-standard, ease) both; background: rgba(255,255,255,.055); border: 1px solid var(--ee-border); border-radius: 18px; display: grid; gap: .25rem; min-height: 6rem; padding: .9rem; transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease), border-color var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .workflow li:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    .workflow li:nth-child(2) { animation-delay: 45ms; }
    .workflow li:nth-child(3) { animation-delay: 90ms; }
    .workflow li:nth-child(4) { animation-delay: 135ms; }
    .workflow li:nth-child(5) { animation-delay: 180ms; }
    .workflow li:nth-child(6) { animation-delay: 225ms; }
    .workflow li:nth-child(7) { animation-delay: 260ms; }
    .workflow li strong { color: var(--ee-text); }
    .workflow li span { color: var(--ee-text-soft); }
    .workflow li.disabled { background: rgba(255,255,255,.035); border-style: dashed; opacity: .82; position: relative; }
    .workflow li.disabled::after { background: rgba(244,201,93,.16); border: 1px solid rgba(244,201,93,.28); border-radius: 999px; color: #ffe5a2; content: 'Locked'; font-size: .68rem; font-weight: 900; padding: .22rem .48rem; position: absolute; right: .65rem; top: .65rem; }
    .future-pill { background: rgba(244,201,93,.13); border: 1px solid rgba(244,201,93,.34); border-radius: 999px; color: #ffe5a2; font-weight: 900; padding: .35rem .65rem; }
    .pitch-cards { grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); }
    .pitch-cards article { animation: ee-motion-card-enter var(--ee-duration-slow, 260ms) var(--ee-easing-standard, ease) both; border: 1px solid var(--ee-border); border-radius: 18px; display: grid; gap: .3rem; padding: .9rem; transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .pitch-cards article:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    .pitch-cards span { color: var(--ee-gold); font-size: .72rem; font-weight: 900; text-transform: uppercase; }
    .pitch-cards p { color: var(--ee-text-soft); margin: 0; }
    .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(min(24rem, 100%), 1fr)); }
    .panel { display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 1.5rem); }
    label { color: var(--ee-text-soft); display: grid; font-weight: 800; gap: .4rem; }
    input, select, textarea { background: rgba(255,255,255,.075); border: 1px solid var(--ee-border); border-radius: .9rem; color: var(--ee-text); padding: .75rem .85rem; width: 100%; }
    input:focus, select:focus, textarea:focus, button:focus-visible, a:focus-visible { outline: 3px solid rgba(92,200,255,.25); outline-offset: 3px; }
    .checklist { background: rgba(255,255,255,.045); border: 1px solid var(--ee-border); border-radius: 1rem; display: grid; gap: .35rem; padding: .9rem; }
    .checklist p { font-weight: 900; margin: 0; }
    .status { animation: ee-motion-slide-up var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease) both; background: rgba(92,200,255,.12); border-left: 4px solid var(--ee-azure); border-radius: .75rem; color: var(--ee-text); font-weight: 800; padding: .9rem 1rem; }
    .product-list { display: grid; gap: .75rem; }
    .product-list article { align-items: center; background: rgba(255,255,255,.045); border: 1px solid var(--ee-border); border-radius: 1rem; display: flex; gap: 1rem; justify-content: space-between; padding: 1rem; transition: transform var(--ee-duration-base, 180ms) var(--ee-easing-standard, ease); }
    .product-list article:hover { transform: var(--ee-hover-lift, translateY(-3px)); }
    .runtime { color: var(--ee-azure) !important; font-weight: 800; }
    @media (prefers-reduced-motion: reduce) { .workflow li, .pitch-cards article, .status { animation: none; } .workflow li:hover, .pitch-cards article:hover, .product-list article:hover { transform: none; } }
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
  productSubtitle = '';
  productDescription = '';
  pricingModel = 'internal';
  visibility = 'draft';
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
      subtitle: this.productSubtitle || null,
      description: this.productDescription || null,
      status: 'draft',
      review_state: this.selectedCourseId ? 'runtime_authoritative' : 'not_reviewed',
      access_state: this.selectedCourseId ? 'existing_runtime' : 'private',
      visibility: this.visibility,
      pricing_model: this.pricingModel,
      price_placeholder: this.pricingModel === 'paid' ? 'Price placeholder - checkout not connected' : null,
      currency: this.pricingModel === 'paid' ? 'USD' : null,
      metadata: { source: 'product_studio_phase_3', ai_generation: 'not_implemented', checkout: 'not_implemented' },
    }).subscribe({
      next: product => {
        this.statusMessage = `Product shell ready: ${product.title}`;
        this.productTitle = '';
        this.productSubtitle = '';
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
