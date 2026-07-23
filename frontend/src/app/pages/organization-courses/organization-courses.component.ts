import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { AccessGrant, Product } from '../../models/v2-platform.model';
import { V2PlatformService } from '../../services/v2-platform.service';

@Component({
  selector: 'app-organization-courses',
  standalone: true,
  imports: [CommonModule, FormsModule, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './organization-courses.component.html',
  styleUrl: './organization-courses.component.scss',
})
export class OrganizationCoursesComponent implements OnInit {
  products: Product[] = [];
  grants: AccessGrant[] = [];
  searchTerm = '';
  typeFilter = '';
  loading = true;
  loadError = '';

  constructor(private readonly v2Platform: V2PlatformService) {}

  ngOnInit(): void { this.load(); }

  get learningProducts(): Product[] {
    return this.products.filter(product => ['course', 'learning_path', 'certification'].includes(product.product_type));
  }

  get types(): string[] { return [...new Set(this.learningProducts.map(product => product.product_type))].sort(); }

  get filteredProducts(): Product[] {
    const search = this.searchTerm.trim().toLowerCase();
    return this.learningProducts.filter(product =>
      (!this.typeFilter || product.product_type === this.typeFilter) &&
      (!search || product.title.toLowerCase().includes(search) || (product.description || '').toLowerCase().includes(search))
    );
  }

  load(): void {
    this.loading = true;
    this.loadError = '';
    forkJoin({ products: this.v2Platform.getProducts(), grants: this.v2Platform.getAccessGrants() }).subscribe({
      next: result => { this.products = result.products; this.grants = result.grants; this.loading = false; },
      error: () => { this.products = []; this.grants = []; this.loading = false; this.loadError = 'We could not load organization course availability. No access changed.'; },
    });
  }

  activeGrantCount(productId: string): number { return this.grants.filter(grant => grant.product_id === productId && grant.status === 'active').length; }
  label(value: string): string { return value.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase()); }
}
