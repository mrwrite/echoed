import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { CourseDraft } from './models/course-draft.model';

@Injectable({ providedIn: 'root' })
export class CourseWizardService {
  private draft = new BehaviorSubject<CourseDraft>({
    title: '',
    description: '',
    units: []
  });

  draft$ = this.draft.asObservable();

  updateDraft(data: Partial<CourseDraft>) {
    this.draft.next({ ...this.draft.value, ...data });
  }

  resetDraft() {
    this.draft.next({
      title: '',
      description: '',
      units: []
    });
  }

 get draftValue(): CourseDraft {
    return this.draft.value;
  }
}
