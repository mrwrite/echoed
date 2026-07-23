import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-route-load-error',
  standalone: true,
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <main class="route-load-error" aria-labelledby="route-load-error-title">
      <section role="alert">
        <p class="route-load-error__eyebrow">Connection interrupted</p>
        <h1 id="route-load-error-title">This part of EchoEd could not load</h1>
        <p>
          Your account and progress are unchanged. Check your connection, then retry the page.
        </p>
        <div class="route-load-error__actions">
          <button type="button" (click)="retry()">Retry</button>
          <a routerLink="/">Return to EchoEd home</a>
        </div>
      </section>
    </main>
  `,
  styles: `
    :host {
      display: block;
      min-height: 100%;
    }

    .route-load-error {
      display: grid;
      min-height: 100vh;
      place-items: center;
      padding: 1.5rem;
      background: var(--echo-surface-canvas, #f7f5ef);
    }

    section {
      width: min(100%, 36rem);
      padding: clamp(1.5rem, 5vw, 3rem);
      border: 1px solid var(--echo-border-default, #d8d5cc);
      border-radius: 1rem;
      background: var(--echo-surface-panel, #fff);
      box-shadow: 0 1rem 3rem rgb(27 39 33 / 10%);
    }

    .route-load-error__eyebrow {
      margin: 0 0 0.5rem;
      color: var(--echo-text-accent, #276447);
      font-weight: 700;
    }

    h1 {
      margin-block: 0 0.75rem;
    }

    .route-load-error__actions {
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      margin-top: 1.5rem;
    }

    button,
    a {
      display: inline-flex;
      min-height: 44px;
      align-items: center;
      justify-content: center;
      padding: 0.65rem 1rem;
      border-radius: 0.5rem;
      font: inherit;
      font-weight: 700;
    }

    button {
      border: 0;
      color: #fff;
      background: var(--echo-action-primary, #276447);
      cursor: pointer;
    }

    a {
      color: var(--echo-text-primary, #17221c);
    }
  `,
})
export class RouteLoadErrorComponent {
  retry(): void {
    window.location.reload();
  }
}
