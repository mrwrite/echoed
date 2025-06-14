// models/student-course.ts

export interface StudentCourse {
    id: string;            // unique StudentCourse ID (optional - sometimes DB driven)
    courseId: string;       // the ID of the base Course
    userId: string;         // the ID of the student
    enrolledDate: Date;
    currentUnitId?: string; // optional: the current Unit ID they are on
    currentLessonId?: string; // optional: the current Lesson ID they are on
    completedLessonIds: string[]; // list of finished Lesson IDs
    progress: number;       // % completion of the course
    isCompleted: boolean;
  }
  