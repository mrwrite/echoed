import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';

import { EchoButtonComponent } from '../../components/echo-button/echo-button.component';
import { Assessment, Certification, Program } from '../../models/program';
import { ProgramsService } from '../../services/programs.service';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-programs',
  standalone: true,
  imports: [CommonModule, RouterLink, EchoButtonComponent],
  templateUrl: './programs.component.html',
  styleUrl: './programs.component.scss'
})
export class ProgramsComponent implements OnInit {
  programs: Program[] = [];
  assessmentsByProgram: Record<string, Assessment[]> = {};
  certificationsByProgram: Record<string, Certification[]> = {};
  loading = true;

  constructor(
    private programsService: ProgramsService,
    private toastService: ToastService,
  ) {}

  ngOnInit(): void {
    this.loadPrograms();
  }

  enroll(programId: string): void {
    this.programsService.enrollInProgram(programId).subscribe({
      next: () => {
        this.toastService.show('Program enrollment saved.', 'success');
        this.loadPrograms();
      },
      error: () => {
        this.toastService.show('Unable to enroll in this program right now.', 'error');
      }
    });
  }

  private loadPrograms(): void {
    this.loading = true;
    this.programsService.getPrograms().subscribe({
      next: (programs) => {
        this.programs = programs;
        if (programs.length === 0) {
          this.assessmentsByProgram = {};
          this.certificationsByProgram = {};
          this.loading = false;
          return;
        }

        forkJoin(
          programs.map(program =>
            forkJoin({
              assessments: this.programsService.getAssessments({ programId: program.id }),
              certifications: this.programsService.getCertifications(program.id),
            })
          )
        ).subscribe({
          next: (details) => {
            this.assessmentsByProgram = {};
            this.certificationsByProgram = {};
            details.forEach((detail, index) => {
              const programId = programs[index].id;
              this.assessmentsByProgram[programId] = detail.assessments;
              this.certificationsByProgram[programId] = detail.certifications;
            });
            this.loading = false;
          },
          error: () => {
            this.loading = false;
            this.toastService.show('Programs loaded, but some supporting details failed to load.', 'error');
          }
        });
      },
      error: () => {
        this.loading = false;
        this.toastService.show('Unable to load programs right now.', 'error');
      }
    });
  }
}
