import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { AccessGrant, Product } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-access-grants',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <section class="access" aria-labelledby="access-title">
      <header>
        <p>Access Grants</p>
        <h1 id="access-title">Product access management</h1>
        <span>Grant product-level access without changing course enrollment, checkout, or lesson governance.</span>
      </header>

      <form class="panel" (ngSubmit)="createGrant()" aria-label="Create access grant">
        <h2>Create manual grant</h2>
        <label>
          Product
          <select name="productId" [(ngModel)]="form.product_id" required>
            <option value="">Select product</option>
            <option *ngFor="let product of products" [value]="product.id">{{ product.title }}</option>
          </select>
        </label>
        <label>
          Learner user ID
          <input name="userId" [(ngModel)]="form.user_id" required placeholder="User UUID" />
        </label>
        <label>
          Grant type
          <select name="grantType" [(ngModel)]="form.grant_type">
            <option *ngFor="let type of grantTypes" [value]="type">{{ label(type) }}</option>
          </select>
        </label>
        <label>
          Status
          <select name="status" [(ngModel)]="form.status">
            <option value="active">Active</option>
            <option value="pending">Pending</option>
          </select>
        </label>
        <label>
          Source
          <input name="source" [(ngModel)]="form.source" />
        </label>
        <label>
          Starts at
          <input name="startsAt" type="datetime-local" [(ngModel)]="form.starts_at" />
        </label>
        <label>
          Expires at
          <input name="expiresAt" type="datetime-local" [(ngModel)]="form.expires_at" />
        </label>
        <button type="submit">Create grant</button>
        <p class="message" *ngIf="message">{{ message }}</p>
      </form>

      <article class="panel">
        <div class="panel__heading">
          <h2>Existing grants</h2>
          <button type="button" (click)="loadGrants()">Refresh</button>
        </div>
        <div class="empty" *ngIf="!grants.length">No access grants found.</div>
        <div class="grant" *ngFor="let grant of grants">
          <div>
            <h3>{{ productTitle(grant.product_id) }}</h3>
            <p>{{ grant.user_id }}</p>
          </div>
          <dl>
            <div>
              <dt>Type</dt>
              <dd>{{ label(grant.grant_type) }}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{{ label(grant.status) }}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>{{ grant.source }}</dd>
            </div>
          </dl>
          <button type="button" [disabled]="grant.status === 'revoked'" (click)="revoke(grant)">Revoke</button>
        </div>
      </article>
    </section>
  `,
  styles: [`
    .access { color: #102033; display: grid; gap: 1rem; padding: clamp(1rem, 3vw, 2rem); }
    header, .panel { background: #fff; border: 1px solid #d8e1ea; border-radius: 8px; box-shadow: 0 14px 32px rgba(16,32,51,.08); padding: clamp(1rem, 3vw, 1.5rem); }
    header p { color: #0f766e; font-size: .76rem; font-weight: 900; letter-spacing: .12em; margin: 0 0 .35rem; text-transform: uppercase; }
    h1, h2, h3 { letter-spacing: 0; margin: 0; }
    h1 { font-size: clamp(2rem, 5vw, 3rem); line-height: 1; }
    header span, .message, .empty, .grant p, dd { color: #526273; }
    form.panel { display: grid; gap: .85rem; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); }
    form h2, form button, .message { grid-column: 1 / -1; }
    label { color: #334155; display: grid; font-weight: 900; gap: .35rem; }
    input, select { border: 1px solid #cbd5e1; border-radius: 6px; color: #102033; font: inherit; padding: .65rem .75rem; }
    button { background: #102033; border: 1px solid #102033; border-radius: 6px; color: #fff; cursor: pointer; font: inherit; font-weight: 900; padding: .65rem .85rem; width: fit-content; }
    button:disabled { background: #e2e8f0; border-color: #cbd5e1; color: #64748b; cursor: default; }
    .panel { display: grid; gap: .9rem; }
    .panel__heading { align-items: center; display: flex; justify-content: space-between; gap: 1rem; }
    .grant { border: 1px solid #d8e1ea; border-radius: 8px; display: grid; gap: .75rem; padding: 1rem; }
    dl { display: grid; gap: .55rem; grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr)); margin: 0; }
    dt { color: #334155; font-size: .75rem; font-weight: 900; text-transform: uppercase; }
    dd { margin: .15rem 0 0; }
    input:focus-visible, select:focus-visible, button:focus-visible { outline: 3px solid rgba(15,118,110,.25); outline-offset: 3px; }
  `]
})
export class AccessGrantsComponent implements OnInit {
  private readonly v2Platform = inject(V2PlatformService);

  readonly grantTypes = ['manual', 'enrollment', 'membership', 'purchase', 'organization', 'invitation'];
  grants: AccessGrant[] = [];
  products: Product[] = [];
  message = '';
  form = {
    user_id: '',
    product_id: '',
    grant_type: 'manual',
    status: 'active',
    source: 'manual',
    starts_at: '',
    expires_at: '',
  };

  ngOnInit(): void {
    this.v2Platform.getProducts().subscribe(products => {
      this.products = products;
    });
    this.loadGrants();
  }

  createGrant(): void {
    const product = this.products.find(item => item.id === this.form.product_id);
    this.v2Platform.createAccessGrant({
      user_id: this.form.user_id,
      product_id: this.form.product_id,
      workspace_id: product?.workspace_id,
      project_id: product?.project_id,
      grant_type: this.form.grant_type,
      status: this.form.status,
      source: this.form.source || this.form.grant_type,
      starts_at: this.form.starts_at ? new Date(this.form.starts_at).toISOString() : null,
      expires_at: this.form.expires_at ? new Date(this.form.expires_at).toISOString() : null,
      metadata: { created_from: 'workspace_access_view' },
    }).subscribe({
      next: () => {
        this.message = 'Access grant saved.';
        this.loadGrants();
      },
      error: () => {
        this.message = 'Unable to save access grant.';
      },
    });
  }

  revoke(grant: AccessGrant): void {
    this.v2Platform.revokeAccessGrant(grant.id).subscribe({
      next: () => {
        this.message = 'Access grant revoked.';
        this.loadGrants();
      },
      error: () => {
        this.message = 'Unable to revoke access grant.';
      },
    });
  }

  loadGrants(): void {
    this.v2Platform.getAccessGrants().subscribe(grants => {
      this.grants = grants;
    });
  }

  productTitle(productId: string): string {
    return this.products.find(product => product.id === productId)?.title || productId;
  }

  label(value: string): string {
    return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
  }
}
