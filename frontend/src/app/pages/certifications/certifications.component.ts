import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';

import { StudentCertification } from '../../models/program';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-certifications',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './certifications.component.html',
  styleUrl: './certifications.component.scss'
})
export class CertificationsComponent implements OnInit {
  certifications: StudentCertification[] = [];
  loading = true;

  constructor(
    private programsService: ProgramsService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.programsService.getMyCertifications().subscribe({
      next: (certifications) => {
        this.certifications = certifications;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.toastService.show('Unable to load certifications right now.', 'error');
      }
    });
  }
}
