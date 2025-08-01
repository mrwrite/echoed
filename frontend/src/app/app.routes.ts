import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { UserDashboardComponent } from './pages/user-dashboard/user-dashboard.component';
import { RegistrationComponent } from './pages/registration/registration.component';
import { HomeComponent } from './pages/home/home.component';
import { CourseWizardComponent } from './pages/admin/course-wizard/course-wizard.component';
import { EchoedRoleSelectorComponent } from './pages/user-dashboard/echoed-role-selector/echoed-role-selector.component';
import { LessonViewComponent } from './pages/lesson-view.component';
import { LandingComponent } from './pages/landing/landing.component';
import { AvailableCoursesComponent } from './pages/available-courses/available-courses.component';
import { AdminUsersComponent } from './pages/admin-users/admin-users.component';
import { AdminCoursesComponent } from './pages/admin-courses/admin-courses.component';
import { AdminBadgesComponent } from './pages/admin-badges/admin-badges.component';
import { RoleGuard } from './guards/role.guard';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'login', component: LoginComponent },
  { path: 'registration', component: RegistrationComponent },
  {
    path: 'home',
    component: HomeComponent,
    children: [
      {
        path: '',
        component: UserDashboardComponent,
        children: [
          { path: '', component: EchoedRoleSelectorComponent },
          {
            path: 'courses/new',
            component: CourseWizardComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin', 'teacher'] }
          },
          {
            path: 'courses/:courseId/edit',
            component: CourseWizardComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin', 'teacher'] }
          },
          { path: 'courses', component: AvailableCoursesComponent },
          {
            path: 'admin/courses',
            component: AdminCoursesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'admin/badges',
            component: AdminBadgesComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          {
            path: 'admin/users',
            component: AdminUsersComponent,
            canActivate: [RoleGuard],
            data: { roles: ['admin'] }
          },
          { path: 'lesson/:id', component: LessonViewComponent },
        ]
      }
    ]
  },
  { path: '**', redirectTo: '' }
];
