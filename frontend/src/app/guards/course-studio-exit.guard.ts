import { CanDeactivateFn } from '@angular/router';
import { CourseStudioComponent } from '../pages/course-studio/course-studio.component';

export const courseStudioExitGuard: CanDeactivateFn<CourseStudioComponent> = component =>
  !component.dirty || confirm('This course still has unsaved changes. Leave without saving them?');
