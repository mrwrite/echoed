import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface AfricaMapRegion {
  id: string;
  label: string;
  fact: string;
  focus?: string[];
  x: number;
  y: number;
}

export interface AfricaMapExplorerData {
  title?: string;
  prompt?: string;
  contextImageUrl?: string;
  referenceImageUrl?: string;
  referenceImageAlt?: string;
  regions?: AfricaMapRegion[];
}

@Component({
  selector: 'app-africa-map-explorer',
  standalone: true,
  imports: [CommonModule],
  template: `
    <section class="space-y-4">
      <div class="rounded-2xl border border-slate-200 bg-white p-4 md:p-5">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
              {{ data?.title || 'Africa map explorer' }}
            </p>
            <h4 class="mt-1 text-lg font-semibold text-ink">
              Explore Africa by region
            </h4>
          </div>
          <span class="badge-soft">Interactive map</span>
        </div>
        <p *ngIf="data?.prompt" class="mt-3 text-sm leading-6 text-slate-700">
          {{ data?.prompt }}
        </p>
        <div class="mt-4 grid gap-4 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)]">
          <article *ngIf="contextImageUrl" class="rounded-2xl border border-slate-200 bg-slate-50 p-3">
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">World context</p>
            <img
              [src]="contextImageUrl"
              [alt]="data?.referenceImageAlt || 'Africa in world context'"
              class="mt-3 w-full rounded-xl border border-slate-200 bg-white object-contain"
            />
          </article>

          <article class="rounded-2xl border border-slate-200 bg-slate-50 p-3">
            <p class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Reference map</p>
            <div class="relative mt-3 overflow-hidden rounded-xl border border-slate-200 bg-white">
              <img
                [src]="referenceImageUrl"
                [alt]="data?.referenceImageAlt || 'Africa reference map'"
                class="block h-auto w-full object-contain"
              />
              <button
                *ngFor="let region of regions"
                type="button"
                class="absolute -translate-x-1/2 -translate-y-1/2 rounded-full border px-3 py-1 text-[0.72rem] font-bold shadow-sm transition"
                [style.left.%]="region.x"
                [style.top.%]="region.y"
                [ngClass]="selectedRegion?.id === region.id ? 'border-primary bg-primary text-white' : 'border-white bg-white/95 text-slate-700 hover:bg-primary/10'"
                (click)="selectRegion(region.id)"
                [attr.aria-pressed]="selectedRegion?.id === region.id"
              >
                {{ region.label }}
              </button>
            </div>
          </article>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-[minmax(0,0.7fr)_minmax(0,1.3fr)]">
        <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4 md:p-5">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Regions</p>
          <div class="mt-3 grid gap-2">
            <button
              *ngFor="let region of regions"
              type="button"
              class="rounded-xl border px-3 py-3 text-left text-sm font-semibold transition"
              [ngClass]="selectedRegion?.id === region.id ? 'border-primary bg-primary/5 text-primary' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'"
              (click)="selectRegion(region.id)"
            >
              {{ region.label }}
            </button>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-4 md:p-5" aria-live="polite">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary">Map reading note</p>
          <h5 class="mt-1 text-lg font-semibold text-ink">
            {{ selectedRegion?.label || 'Choose a region' }}
          </h5>
          <p class="mt-3 text-sm leading-6 text-slate-700">
            {{ selectedRegion?.fact || 'Select a region to see one map-reading clue and a question to discuss.' }}
          </p>
          <ul *ngIf="selectedRegion?.focus?.length" class="mt-4 grid gap-2">
            <li *ngFor="let item of selectedRegion?.focus" class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-700">
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </section>
  `,
})
export class AfricaMapExplorerComponent {
  @Input() data: AfricaMapExplorerData | null = null;

  get regions(): AfricaMapRegion[] {
    return this.data?.regions || [];
  }

  get contextImageUrl(): string {
    return this.data?.contextImageUrl || '/assets/maps/world-context.svg';
  }

  get referenceImageUrl(): string {
    return this.data?.referenceImageUrl || '/assets/maps/africa-reference.svg';
  }

  selectedRegion: AfricaMapRegion | null = null;

  selectRegion(regionId: string): void {
    this.selectedRegion = this.regions.find((region) => region.id === regionId) || null;
  }
}
