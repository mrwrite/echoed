import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { FormsModule } from '@angular/forms';
import { Subscription, switchMap } from 'rxjs';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { Badge } from '../../models/badge';
import { BadgesService } from '../../services/badges.service';
import { PermissionsService } from '../../services/permissions.service';

@Component({
  selector: 'admin-badges-page',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './admin-badges.component.html',
  styleUrl: './admin-badges.component.scss'
})
export class AdminBadgesComponent implements OnInit, OnDestroy {
  badges: Badge[] = [];
  badgeForm: FormGroup;
  selectedFile: File | null = null;
  search = '';
  role = '';
  loading = true;
  failed = false;
  submitting = false;
  submitError = '';
  successMessage = '';
  private readonly subscriptions = new Subscription();

  constructor(private readonly badgesService: BadgesService, fb: FormBuilder, permissions: PermissionsService) {
    this.badgeForm = fb.group({ title: ['', [Validators.required, Validators.maxLength(120)]], description: ['', Validators.maxLength(500)], image_url: [''] });
    this.subscriptions.add(permissions.user$.subscribe(user => this.role = user?.role ?? ''));
  }

  ngOnInit(): void { this.loadBadges(); }
  ngOnDestroy(): void { this.subscriptions.unsubscribe(); }
  get canCreate(): boolean { return this.role === 'admin'; }
  get filteredBadges(): Badge[] { const q = this.search.trim().toLowerCase(); return this.badges.filter(badge => !q || badge.title.toLowerCase().includes(q)); }

  loadBadges(): void {
    this.loading = true; this.failed = false;
    this.subscriptions.add(this.badgesService.getBadges().subscribe({ next: badges => { this.badges = badges; this.loading = false; }, error: () => { this.failed = true; this.loading = false; } }));
  }

  onFileSelected(event: Event): void { this.selectedFile = (event.target as HTMLInputElement).files?.[0] ?? null; }

  onSubmit(): void {
    if (!this.canCreate || this.badgeForm.invalid || this.submitting) { this.badgeForm.markAllAsTouched(); return; }
    this.submitting = true; this.submitError = ''; this.successMessage = '';
    const create = (imageUrl?: string) => this.badgesService.createBadge({ ...this.badgeForm.value, image_url: imageUrl || this.badgeForm.value.image_url || undefined });
    const request = this.selectedFile ? this.badgesService.uploadBadgeImage(this.selectedFile).pipe(switchMap(response => create(response.file_path))) : create();
    this.subscriptions.add(request.subscribe({
      next: badge => { this.badges = [...this.badges, badge]; this.badgeForm.reset(); this.selectedFile = null; this.submitting = false; this.successMessage = `${badge.title} was created.`; },
      error: () => { this.submitting = false; this.submitError = 'The badge was not created. Review the fields and try again.'; },
    }));
  }
}
