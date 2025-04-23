import { 
  Component, 
  Input, 
  ElementRef, 
  HostListener, 
  ViewChild 
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../models/user-info';
import {
  trigger,
  style,
  transition,
  animate
} from '@angular/animations';
import { AuthService } from '../../services/auth.service';
import { Router, RouterModule } from '@angular/router';


@Component({
  selector: 'echo-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './echo-header.component.html',
  styleUrl: './echo-header.component.scss',
  animations: [
    trigger('menuAnim', [
      transition(':enter', [
        style({ opacity: 0, transform: 'scale(0.95)' }),
        animate('150ms ease-out', style({ opacity: 1, transform: 'scale(1)' })),
      ]),
      transition(':leave', [
        animate('100ms ease-in', style({ opacity: 0, transform: 'scale(0.95)' })),
      ]),
    ]),
  ],
})

export class EchoHeaderComponent {
  @Input() userinfo!: UserInfo;
  menuOpen: boolean = false;

  @ViewChild('menuContainer') menuContainer!: ElementRef;

  constructor(private authService: AuthService,
    private router: Router
  ) {}

  getInitials(): string {
    return this.userinfo?.fullname
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase();
  }

  toggleMenu(): void {
    this.menuOpen = !this.menuOpen;
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }

  @HostListener('document:click', ['$event.target'])
  onClickOutside(targetElement: HTMLElement) {
    if (this.menuContainer && !this.menuContainer.nativeElement.contains(targetElement)) {
      this.menuOpen = false;
    }
  }
}
