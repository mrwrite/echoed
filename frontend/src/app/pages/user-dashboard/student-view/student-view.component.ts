import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UserInfo } from '../../../models/user-info';
import { Course } from '../../../models/course';
import { StudentCourse } from '../../../models/student-course';

@Component({
  selector: 'echoed-student-view',
  standalone: true,
  imports: [ CommonModule ],
  templateUrl: './student-view.component.html',
  styleUrl: './student-view.component.scss'
})
export class StudentViewComponent implements OnInit {
  @Input() userInfo!: UserInfo;
  studentCourses: StudentCourse[] = [];

  ngOnInit(): void {
    this.loadStudentCourses();
  }

  loadStudentCourses(){
    this.studentCourses = [
      {
        id: 'enroll-1',
        courseId: 'course-1',
        userId: this.userInfo.user_id,
        enrolledDate: new Date(),
        currentUnitId: 'unit-2',
        currentLessonId: 'lesson-4',
        completedLessonIds: ['lesson-1', 'lesson-2', 'lesson-3'],
        progress: 65,
        isCompleted: false
      }
    ];
  }

  startCourse(course: StudentCourse){
    
  }
}
