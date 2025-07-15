import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { StudentCourse } from '../../../models/student-course';
import { CoursesService } from '../../../services/courses.service';
import { Router } from '@angular/router';
import { Lesson } from '../../../models/lesson';
import { LessonViewerComponent } from "../../../shared/lesson-viewer.component";
import { EchoButtonComponent } from '../../../components/echo-button/echo-button.component';
import { StudentCourseCardComponent } from '../../../components/student-course-card/student-course-card.component';
import { AchievementItemComponent } from '../../../components/achievement-item/achievement-item.component';
import { Course } from '../../../models/course';
import { StudentCourseWithDetails } from '../../../models/student-course-with-details.model';
import { ToastService } from '../../../services/toast.service';

@Component({
  selector: 'echoed-student-view',
  standalone: true,
  imports: [
    CommonModule,
    LessonViewerComponent,
    EchoButtonComponent,
    StudentCourseCardComponent,
    AchievementItemComponent,
  ],
  templateUrl: './student-view.component.html',
  styleUrl: './student-view.component.scss'
})
export class StudentViewComponent implements OnInit {
  @Input() userInfo!: UserInfo;
  studentCourses: StudentCourseWithDetails[] = [];
  activeStudentCourse?: StudentCourseWithDetails;
  currentLesson?: Lesson;
  showLesson = false;
  availableCourses: Course[] = [];
  

  constructor(private coursesService: CoursesService,
              private router: Router,
              private toastService: ToastService
  ) { }

  ngOnInit(): void {
    this.loadStudentCourses();    
  }

  loadAvailableCourses(): void {
  this.coursesService.getCourses().subscribe({
    next: (courses) => {
      const enrolledCourseIds = this.studentCourses.map(sc => sc.course_id);
      this.availableCourses = courses.filter(course => !enrolledCourseIds.includes(course.id));
    },
    error: (err) => {
      console.error('Failed to load available courses', err);
    }
  });
}

  loadStudentCourses(): void {
    this.coursesService.getStudentCourses().subscribe({
    next: (courses) => {
      this.studentCourses = courses;
      this.loadAvailableCourses(); // Refresh available courses after loading student courses
    },
    error: (err) => {
      console.error('Failed to load student courses', err);
    }
  });
  }

  onLessonCompleted(): void {
  if (!this.currentLesson || !this.activeStudentCourse) return;
  

  if (this.activeStudentCourse.unitProgressId) {
    this.coursesService.markSegmentCompleted(
    this.activeStudentCourse.unitProgressId,
    this.currentLesson.id
  ).subscribe({
    next: () => {
      this.toastService.show('Lesson completed! Progress saved.', 'success');
      this.showLesson = false;
      this.currentLesson = undefined;
    },
    error: () => {
      this.toastService.show('There was an error saving your progress.', 'error');
    }
  });
  }
  
}

enrollInCourse(courseId: string): void {
  this.coursesService.enrollInCourse(courseId).subscribe({
    next: () => {
      this.toastService.show('Enrollment successful!', 'success');
      this.loadStudentCourses();
      this.loadAvailableCourses();
    },
    error: (err) => {
      console.error('Enrollment failed', err);
      this.toastService.show('Enrollment failed. You may already be enrolled.', 'error');
    }
  });
}


  startCourse(course: StudentCourseWithDetails): void {
    this.coursesService.startCourse({ course_id: course.course.id }).subscribe(segment => {
      this.router.navigate(['/home/lesson', segment.unit_progress_id || '']);
    });
  }
}
