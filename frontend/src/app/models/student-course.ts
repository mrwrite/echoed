// models/student-course.ts

export interface StudentCourse {
    id: string;            
    courseId: string;       
    userId: string;         
    enrolledDate: Date;
    currentUnitId?: string; 
    currentLessonId?: string; 
    completedLessonIds: string[]; 
    progress: number;       
    isCompleted: boolean;
    unitProgressId?: string; 
  }
  