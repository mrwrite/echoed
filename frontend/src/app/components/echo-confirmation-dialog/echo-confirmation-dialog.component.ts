import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-echo-confirmation-dialog',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="open"
      class="echo-dialog-backdrop"
      role="presentation"
      (click)="onBackdropClick()"
    >
      <section
        #dialogPanel
        class="echo-dialog"
        role="dialog"
        aria-modal="true"
        [attr.aria-labelledby]="titleId"
        [attr.aria-describedby]="descriptionId"
        (click)="$event.stopPropagation()"
        tabindex="-1"
      >
        <p class="echo-dialog__eyebrow">{{ variantLabel }}</p>
        <h2 [id]="titleId">{{ title }}</h2>
        <p [id]="descriptionId">{{ description }}</p>

        <div *ngIf="objectName" class="echo-dialog__object">
          <span>Affected item</span>
          <strong>{{ objectName }}</strong>
        </div>

        <p *ngIf="errorMessage" class="echo-dialog__error" role="alert">{{ errorMessage }}</p>

        <div class="echo-dialog__actions">
          <button
            #cancelButton
            type="button"
            class="echo-dialog__button echo-dialog__button--secondary"
            [disabled]="loading"
            (click)="cancel.emit()"
          >
            {{ cancelLabel }}
          </button>
          <button
            type="button"
            class="echo-dialog__button"
            [class.echo-dialog__button--danger]="variant === 'danger'"
            [class.echo-dialog__button--primary]="variant !== 'danger'"
            [disabled]="loading"
            (click)="confirm.emit()"
          >
            {{ loading ? loadingLabel : confirmLabel }}
          </button>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .echo-dialog-backdrop {
      align-items: center;
      background: rgba(16, 32, 51, 0.48);
      display: flex;
      inset: 0;
      justify-content: center;
      padding: var(--ee-space-4, 1rem);
      position: fixed;
      z-index: 100;
    }

    .echo-dialog {
      background: var(--ee-color-surface-raised, #ffffff);
      border: 1px solid var(--ee-color-border-subtle, #dccdb7);
      border-radius: var(--ee-radius-dialog, 0.75rem);
      box-shadow: var(--ee-shadow-overlay, 0 24px 64px rgba(16, 32, 51, 0.24));
      color: var(--ee-color-text-default, #102033);
      display: grid;
      gap: var(--ee-space-4, 1rem);
      max-width: min(32rem, 100%);
      padding: clamp(1rem, 3vw, 1.5rem);
      width: 100%;
    }

    .echo-dialog:focus {
      outline: none;
    }

    .echo-dialog__eyebrow,
    .echo-dialog__object span {
      color: var(--ee-color-action-primary-background, #0f766e);
      font-size: var(--ee-font-size-xs, 0.75rem);
      font-weight: 800;
      letter-spacing: 0.12em;
      margin: 0;
      text-transform: uppercase;
    }

    h2,
    p {
      margin: 0;
    }

    h2 {
      font-size: var(--ee-font-size-2xl, 1.5rem);
      line-height: var(--ee-line-height-heading, 1.25);
    }

    p {
      color: var(--ee-color-text-muted, #40546b);
      line-height: var(--ee-line-height-body, 1.6);
    }

    .echo-dialog__object {
      background: var(--ee-color-surface-subtle, #f4eadc);
      border: 1px solid var(--ee-color-border-subtle, #dccdb7);
      border-radius: var(--ee-radius-card-default, 0.5rem);
      display: grid;
      gap: 0.2rem;
      padding: var(--ee-space-3, 0.75rem);
    }

    .echo-dialog__object strong {
      overflow-wrap: anywhere;
    }

    .echo-dialog__error {
      background: var(--ee-color-status-danger-background, #fff1f3);
      border: 1px solid var(--ee-color-status-danger-border, #ffd9df);
      border-radius: var(--ee-radius-card-default, 0.5rem);
      color: var(--ee-color-status-danger-text, #9f1239);
      padding: var(--ee-space-3, 0.75rem);
    }

    .echo-dialog__actions {
      display: flex;
      flex-wrap: wrap;
      gap: var(--ee-space-3, 0.75rem);
      justify-content: flex-end;
    }

    .echo-dialog__button {
      border-radius: var(--ee-radius-control-default, 0.5rem);
      border: 1px solid transparent;
      cursor: pointer;
      font: inherit;
      font-weight: 800;
      min-height: 2.75rem;
      padding: 0.7rem 1rem;
    }

    .echo-dialog__button:focus-visible {
      outline: var(--ee-focus-ring-width, 2px) solid var(--ee-focus-ring-color, #0f766e);
      outline-offset: var(--ee-focus-ring-offset, 3px);
      box-shadow: var(--ee-focus-ring-shadow, 0 0 0 4px rgba(15, 118, 110, 0.18));
    }

    .echo-dialog__button--secondary {
      background: var(--ee-color-action-secondary-background, #fffdf8);
      border-color: var(--ee-color-action-secondary-border, #cdbda3);
      color: var(--ee-color-action-secondary-text, #102033);
    }

    .echo-dialog__button--primary {
      background: var(--ee-color-action-primary-background, #0f766e);
      border-color: var(--ee-color-action-primary-border, #0f766e);
      color: var(--ee-color-action-primary-text, #ffffff);
    }

    .echo-dialog__button--danger {
      background: var(--ee-color-action-danger-background, #be123c);
      border-color: var(--ee-color-action-danger-border, #be123c);
      color: var(--ee-color-action-danger-text, #ffffff);
    }

    .echo-dialog__button:disabled {
      cursor: wait;
      opacity: 0.68;
    }
  `],
})
export class EchoConfirmationDialogComponent implements AfterViewInit, OnChanges {
  @Input() open = false;
  @Input() title = 'Confirm action';
  @Input() description = 'Review the consequences before continuing.';
  @Input() objectName = '';
  @Input() confirmLabel = 'Confirm';
  @Input() cancelLabel = 'Cancel';
  @Input() loadingLabel = 'Working...';
  @Input() loading = false;
  @Input() errorMessage = '';
  @Input() variant: 'default' | 'danger' | 'publish' = 'default';
  @Output() confirm = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  @ViewChild('dialogPanel') dialogPanel?: ElementRef<HTMLElement>;
  @ViewChild('cancelButton') cancelButton?: ElementRef<HTMLButtonElement>;

  readonly titleId = `echo-confirm-title-${Math.random().toString(36).slice(2)}`;
  readonly descriptionId = `echo-confirm-description-${Math.random().toString(36).slice(2)}`;
  private previouslyFocused: HTMLElement | null = null;

  get variantLabel(): string {
    switch (this.variant) {
      case 'danger':
        return 'Destructive action';
      case 'publish':
        return 'Publishing confirmation';
      default:
        return 'Confirmation';
    }
  }

  ngAfterViewInit(): void {
    this.focusDialog();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['open']) {
      if (this.open) {
        this.previouslyFocused = document.activeElement as HTMLElement | null;
        queueMicrotask(() => this.focusDialog());
      } else {
        this.restoreFocus();
      }
    }
  }

  onBackdropClick(): void {
    if (!this.loading) {
      this.cancel.emit();
    }
  }

  @HostListener('document:keydown', ['$event'])
  onKeydown(event: KeyboardEvent): void {
    if (!this.open) {
      return;
    }

    if (event.key === 'Escape' && !this.loading) {
      event.preventDefault();
      this.cancel.emit();
      return;
    }

    if (event.key === 'Tab') {
      this.trapFocus(event);
    }
  }

  private focusDialog(): void {
    if (this.open) {
      this.cancelButton?.nativeElement.focus();
    }
  }

  private restoreFocus(): void {
    this.previouslyFocused?.focus?.();
    this.previouslyFocused = null;
  }

  private trapFocus(event: KeyboardEvent): void {
    const focusable = this.dialogPanel?.nativeElement.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
    );

    if (!focusable?.length) {
      event.preventDefault();
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
}
