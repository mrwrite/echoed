import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { Router } from '@angular/router';

export interface DemoTourStep {
  id: string;
  title: string;
  description: string;
  route: string;
}

interface DemoTourState {
  active: boolean;
  index: number;
}

@Injectable({ providedIn: 'root' })
export class DemoTourService {
  private readonly steps: DemoTourStep[] = [
    {
      id: 'landing',
      title: 'Landing page',
      description: 'This is the community page for educators, families, organizers, and contributors to explore the mission.',
      route: '/',
    },
    {
      id: 'login',
      title: 'Secure login',
      description: 'Sign in securely as a student, teacher, or admin to access the experience.',
      route: '/login',
    },
    {
      id: 'student-dashboard',
      title: 'Student dashboard',
      description: 'View progress, streaks, and jump into a guided lesson.',
      route: '/home',
    },
    {
      id: 'teacher-dashboard',
      title: 'Teacher center',
      description: 'Monitor classes, manage courses, and start live lessons.',
      route: '/home',
    },
    {
      id: 'admin-dashboard',
      title: 'Admin control',
      description: 'Review platform health, users, and content quality.',
      route: '/home',
    },
    {
      id: 'lesson-viewer',
      title: 'Lesson viewer',
      description: 'See the immersive learning experience with activities and progress tracking.',
      route: '/home/lesson/demo',
    },
  ];

  private state$ = new BehaviorSubject<DemoTourState>({ active: false, index: 0 });

  constructor(private router: Router) {}

  get stepsList(): DemoTourStep[] {
    return this.steps;
  }

  get stateChanges() {
    return this.state$.asObservable();
  }

  get currentStep(): DemoTourStep | null {
    const { index, active } = this.state$.value;
    return active ? this.steps[index] : null;
  }

  startTour() {
    this.state$.next({ active: true, index: 0 });
    this.navigateToCurrent();
  }

  nextStep() {
    const { index } = this.state$.value;
    if (index < this.steps.length - 1) {
      this.state$.next({ active: true, index: index + 1 });
      this.navigateToCurrent();
    } else {
      this.endTour();
    }
  }

  endTour() {
    this.state$.next({ active: false, index: 0 });
  }

  private navigateToCurrent() {
    const step = this.currentStep;
    if (step) {
      this.router.navigateByUrl(step.route);
    }
  }
}
