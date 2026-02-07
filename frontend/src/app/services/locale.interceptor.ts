import { HttpInterceptorFn } from '@angular/common/http';

export const localeInterceptor: HttpInterceptorFn = (req, next) => {
  const locale = localStorage.getItem('locale') || 'en';
  const localeReq = req.clone({
    setHeaders: {
      'Accept-Language': locale
    }
  });
  return next(localeReq);
};
