import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DemoTourService, DemoTourStep } from '../../services/demo-tour.service';

@Component({
  selector: 'app-demo-tour-overlay',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './demo-tour-overlay.component.html',
  styleUrl: './demo-tour-overlay.component.scss'
})
export class DemoTourOverlayComponent {
  constructor(public demoTourService: DemoTourService) {}

  get isActive() {
    return !!this.demoTourService.currentStep;
  }

  get step(): DemoTourStep | null | undefined {
    return this.demoTourService.currentStep;
  }

  get stepIndex() {
    return this.step ? this.demoTourService.stepsList.findIndex(s => s.id === this.step!.id) + 1 : 0;
  }

  get totalSteps() {
    return this.demoTourService.stepsList.length;
  }

  next() {
    this.demoTourService.nextStep();
  }

  close() {
    this.demoTourService.endTour();
  }
}
