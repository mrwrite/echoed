import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';

import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';

@Component({
  selector: 'access-denied-page',
  standalone: true,
  imports: [CommonModule, RouterModule, EchoStatePanelComponent],
  template: `
    <div class="access-denied">
      <app-echo-state-panel
        variant="permission"
        eyebrow="Access denied"
        title="You do not have permission to view this page."
        body="This area is reserved for specific roles. If you believe this is a mistake, reach out to an administrator."
        align="center"
        ariaLabel="Permission denied page"
      ></app-echo-state-panel>
      <div class="access-denied__actions" aria-label="Access denied actions">
        <a routerLink="/home" class="access-denied__primary">Go to dashboard</a>
        <a routerLink="/login" class="access-denied__secondary">Sign in</a>
      </div>
    </div>
  `,
  styles: [`
    .access-denied {
      align-items: center;
      background: var(--ee-color-background-app, #fbf7ef);
      display: flex;
      flex-direction: column;
      gap: var(--ee-space-5, 1.25rem);
      justify-content: center;
      min-height: 100vh;
      padding: var(--ee-space-6, 1.5rem);
    }

    app-echo-state-panel {
      max-width: 36rem;
      width: 100%;
    }

    .access-denied__actions {
      display: flex;
      flex-wrap: wrap;
      gap: var(--ee-space-3, 0.75rem);
      justify-content: center;
    }

    .access-denied__primary,
    .access-denied__secondary {
      border-radius: var(--ee-radius-control-pill, 999px);
      font-weight: 800;
      padding: 0.7rem var(--ee-space-4, 1rem);
      text-decoration: none;
    }

    .access-denied__primary {
      background: var(--ee-color-action-primary-background, #0f766e);
      border: 1px solid var(--ee-color-action-primary-border, #0f766e);
      color: var(--ee-color-action-primary-text, #fff);
    }

    .access-denied__secondary {
      background: var(--ee-color-action-secondary-background, #fffdf8);
      border: 1px solid var(--ee-color-action-secondary-border, #cdbda3);
      color: var(--ee-color-action-secondary-text, #102033);
    }

    .access-denied__primary:focus-visible,
    .access-denied__secondary:focus-visible {
      outline: var(--ee-focus-ring-width, 2px) solid var(--ee-focus-ring-color, #0f766e);
      outline-offset: var(--ee-focus-ring-offset, 3px);
      box-shadow: var(--ee-focus-ring-shadow, 0 0 0 4px rgba(15, 118, 110, 0.18));
    }
  `],
})
export class AccessDeniedComponent {}
