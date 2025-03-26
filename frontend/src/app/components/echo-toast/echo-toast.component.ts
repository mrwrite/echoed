import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-echo-toast',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      *ngIf="visible"
      class="relative fixed bottom-4 right-4 px-4 py-3 pr-10 rounded-lg shadow-lg text-white transition-opacity duration-300"
      [ngClass]="{
        'bg-primary': type === 'info',
        'bg-warn': type === 'warn',
        'bg-tertiary': type === 'error',
        'bg-accent text-black': type === 'success'
      }"
    >
      {{ message }}
      <button
        class="absolute top-1 right-1 text-white/70 hover:text-white text-sm font-bold"
        (click)="dismiss()"
        aria-label="Close"
      >
        &times;
      </button>
    </div>
  `
})
export class EchoToastComponent implements OnInit {
  @Input() message: string = 'This is a toast message';
  @Input() type: 'info' | 'warn' | 'error' | 'success' = 'info';
  @Input() duration: number = 3000; // milliseconds

  visible = true;

  ngOnInit() {
    if (this.duration > 0) {
      setTimeout(() => this.dismiss(), this.duration);
    }
  }

  dismiss() {
    this.visible = false;
  }
}
