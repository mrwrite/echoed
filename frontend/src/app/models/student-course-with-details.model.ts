import { Course } from './course';

export interface StudentCourseWithDetails {
  id: string;
  student_id: string;
  course_id: string;
  enrolled_on: string;
  status: string;
  course: Course;
  unitProgressId?: string;
  /** Progress percentage from 0 to 100 */
  progress?: number;
}
