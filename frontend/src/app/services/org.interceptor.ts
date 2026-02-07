import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { OrganizationService } from './organization.service';

export const orgInterceptor: HttpInterceptorFn = (req, next) => {
  const organizationService = inject(OrganizationService);
  const activeOrgId = organizationService.getActiveOrgId();
  if (activeOrgId) {
    const orgReq = req.clone({
      setHeaders: {
        'X-Org-Id': activeOrgId
      }
    });
    return next(orgReq);
  }
  return next(req);
};
