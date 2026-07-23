import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import {
  provideRouter,
  withComponentInputBinding,
  withNavigationErrorHandler,
} from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';

import { routes } from './app.routes';
import { recoverFromNavigationError } from './routing/navigation-error.handler';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { authInterceptor } from './services/auth.interceptor';
import { orgInterceptor } from './services/org.interceptor';
import { localeInterceptor } from './services/locale.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(
      routes,
      withComponentInputBinding(),
      withNavigationErrorHandler(recoverFromNavigationError),
    ),
    provideHttpClient(withInterceptors([authInterceptor, orgInterceptor, localeInterceptor])),
    provideAnimationsAsync()
  ]
};
