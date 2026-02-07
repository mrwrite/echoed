import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { SectionsService } from '../../services/sections.service';
import { Assignment } from '../../models/section';
import { ToastService } from '../../services/toast.service';

@Component({
  selector: 'app-section-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './section-detail.component.html',
  styleUrl: './section-detail.component.scss'
})
export class SectionDetailComponent implements OnInit {
  sectionId = '';
  assignments: Assignment[] = [];
  targetType = 'lesson';
  targetId = '';
  dueAt = '';
  instructions = '';

  constructor(
    private route: ActivatedRoute,
    private sectionsService: SectionsService,
    private toastService: ToastService
  ) {}

  ngOnInit(): void {
    this.sectionId = this.route.snapshot.paramMap.get('id') || '';
    this.loadAssignments();
  }

  loadAssignments(): void {
    if (!this.sectionId) {
      return;
    }
    this.sectionsService.getAssignments(this.sectionId).subscribe(assignments => {
      this.assignments = assignments;
    });
  }

  createAssignment(): void {
    if (!this.sectionId || !this.targetId) {
      return;
    }
    this.sectionsService.createAssignment(this.sectionId, {
      target_type: this.targetType,
      target_id: this.targetId,
      due_at: this.dueAt || null,
      instructions: this.instructions
    }).subscribe(() => {
      this.toastService.show('Assignment created!', 'success');
      this.targetId = '';
      this.dueAt = '';
      this.instructions = '';
      this.loadAssignments();
    });
  }
}
