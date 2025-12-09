import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { filter } from 'rxjs/operators';

interface Breadcrumb {
  label: string;
  url: string;
}

@Component({
  selector: 'echo-breadcrumbs',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <nav aria-label="breadcrumb" class="text-xs">
      <ol class="flex flex-wrap items-center" *ngIf="breadcrumbs.length > 0">
        <li *ngFor="let crumb of breadcrumbs; let last = last" class="flex items-center">
          <a *ngIf="!last" [routerLink]="crumb.url" class="hover:underline mr-1">
            {{ crumb.label }}
          </a>
          <span *ngIf="last" class="font-semibold mr-1">{{ crumb.label }}</span>
          <span *ngIf="!last" class="mr-1">/</span>
        </li>
      </ol>
    </nav>
  `
})
export class EchoBreadcrumbsComponent implements OnInit {
  breadcrumbs: Breadcrumb[] = [];

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.breadcrumbs = this.buildBreadCrumb(this.router.url);
      });
    this.breadcrumbs = this.buildBreadCrumb(this.router.url);
  }

  private buildBreadCrumb(url: string): Breadcrumb[] {
    const segments = url.split('/').filter(seg => seg);
    const crumbs: Breadcrumb[] = [];
    let accumulated = '';
    for (const segment of segments) {
      accumulated += `/${segment}`;
      const label = segment.replace(/-/g, ' ').replace(/\d+/g, '').trim();
      const display = label ? this.capitalize(label) : segment;
      crumbs.push({ label: this.capitalize(display), url: accumulated });
    }
    return crumbs;
  }

  private capitalize(text: string): string {
    return text.charAt(0).toUpperCase() + text.slice(1);
  }
}
