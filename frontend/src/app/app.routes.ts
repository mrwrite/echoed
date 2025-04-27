import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { UserDashboardComponent } from './pages/user-dashboard/user-dashboard.component';
import { RegistrationComponent } from './pages/registration/registration.component';
import { HomeComponent } from './pages/home/home.component';
import { CourseWizardComponent } from './pages/admin/course-wizard/course-wizard.component';
import { EchoedRoleSelectorComponent } from './pages/user-dashboard/echoed-role-selector/echoed-role-selector.component';

export const routes: Routes = [
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
            { path: '', component: EchoedRoleSelectorComponent },  // <<=== NEW default child
            { path: 'courses/new', component: CourseWizardComponent },
            { path: 'courses/:courseId/edit', component: CourseWizardComponent }
          ]
        }
      ]
    },
    { path: '', redirectTo: '/login', pathMatch: 'full' },
    { path: '**', redirectTo: '/login' }
  ];
  