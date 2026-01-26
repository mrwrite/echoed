import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'access-denied-page',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="min-h-screen flex items-center justify-center bg-slate-50 px-6">
      <div class="max-w-lg bg-white rounded-2xl shadow-soft-card p-8 text-center">
        <p class="text-xs uppercase tracking-[0.3em] text-slate-500">Access denied</p>
        <h1 class="text-2xl font-bold text-ink mt-2">You don’t have permission to view this page.</h1>
        <p class="text-sm text-slate-600 mt-3">
          This area is reserved for specific roles. If you believe this is a mistake, reach out to an admin.
        </p>
        <div class="mt-6 flex flex-wrap gap-3 justify-center">
          <a routerLink="/home" class="px-4 py-2 rounded-full bg-primary text-white font-semibold">Go to dashboard</a>
          <a routerLink="/login" class="px-4 py-2 rounded-full border border-primary text-primary font-semibold">Sign in</a>
        </div>
      </div>
    </div>
  `,
})
export class AccessDeniedComponent {}
