import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EchoToastComponent } from '../echo-toast/echo-toast.component';
import { ToastService, ToastMessage } from '../../services/toast.service';

@Component({
  selector: 'app-echo-toast-container',
  standalone: true,
  imports: [CommonModule, EchoToastComponent],
  template: `
    <div class="fixed bottom-4 right-4 flex flex-col space-y-2">
      <ng-container *ngFor="let toast of toasts">
        <app-echo-toast
          [message]="toast.message"
          [type]="toast.type"
          [duration]="toast.duration"
        ></app-echo-toast>
      </ng-container>
    </div>
  `
})
export class EchoToastContainerComponent {
  toasts: ToastMessage[] = [];

  constructor(private toastService: ToastService) {
    this.toastService.toast$.subscribe(t => (this.toasts = t));
  }
}
