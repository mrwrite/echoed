import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export interface ToastMessage {
  id: number;
  message: string;
  type: 'info' | 'warn' | 'error' | 'success';
  duration: number;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private counter = 0;
  private toastsSubject = new BehaviorSubject<ToastMessage[]>([]);
  toast$ = this.toastsSubject.asObservable();

  show(message: string, type: ToastMessage['type'] = 'info', duration = 3000) {
    const id = this.counter++;
    const toast: ToastMessage = { id, message, type, duration };
    const current = this.toastsSubject.value;
    this.toastsSubject.next([...current, toast]);
    if (duration > 0) {
      setTimeout(() => this.removeToast(id), duration);
    }
  }

  removeToast(id: number) {
    const current = this.toastsSubject.value.filter(t => t.id !== id);
    this.toastsSubject.next(current);
  }
}
