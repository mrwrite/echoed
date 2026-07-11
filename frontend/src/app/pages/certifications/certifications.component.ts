import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';

import { EchoLoadingStateComponent } from '../../components/echo-loading-state/echo-loading-state.component';
import { EchoStatePanelComponent } from '../../components/echo-state-panel/echo-state-panel.component';
import { StudentCertification } from '../../models/program';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-certifications',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoLoadingStateComponent, EchoStatePanelComponent],
  templateUrl: './certifications.component.html',
  styleUrl: './certifications.component.scss'
})
export class CertificationsComponent implements OnInit {
  certifications: StudentCertification[] = [];
  loading = true;
  loadErrorMessage = '';

  constructor(
    private programsService: ProgramsService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.programsService.getMyCertifications().subscribe({
      next: (certifications) => {
        this.certifications = certifications;
        this.loading = false;
        this.loadErrorMessage = '';
      },
      error: () => {
        this.loading = false;
        this.certifications = [];
        this.loadErrorMessage = 'We could not load your certificates right now. Your learning progress was not changed.';
        this.toastService.show('Unable to load certifications right now.', 'error');
      }
    });
  }

  retryLoad(): void {
    this.loading = true;
    this.loadErrorMessage = '';
    this.ngOnInit();
  }
}
