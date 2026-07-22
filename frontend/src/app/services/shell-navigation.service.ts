import { Injectable } from '@angular/core';
import { BootstrapOutcome, PermissionsService } from './permissions.service';

export interface ShellNavItem {
  label: string;
  route: string;
  icon: string;
  permission?: string;
  roles?: string[];
  exact?: boolean;
}

export interface ShellNavSection {
  title: string;
  space: 'learn' | 'teach' | 'studio' | 'organization' | 'admin';
  items: ShellNavItem[];
}

export interface ShellSpaceSummary {
  name: string;
  eyebrow: string;
  description: string;
  canonicalRoute: string;
}

const ROLE_PRIORITY = [
  'admin',
  'super_admin',
  'org_admin',
  'content_admin',
  'teacher',
  'instructor',
  'student',
];

@Injectable({ providedIn: 'root' })
export class ShellNavigationService {
  constructor(private readonly permissionsService: PermissionsService) {}

  readonly sections: ShellNavSection[] = [
    {
      title: 'Learn',
      space: 'learn',
      items: [
        { label: 'Learning Home', route: '/learn', icon: 'Home', roles: ['student'], exact: true },
        { label: 'Courses', route: '/learn/products', icon: 'BookOpen', roles: ['student'] },
        { label: 'Learning Paths', route: '/learn/paths', icon: 'ClipboardList', roles: ['student'] },
        { label: 'Achievements', route: '/learn/certificates', icon: 'Award', roles: ['student'] },
        { label: 'Resources', route: '/learn/resources', icon: 'FileText', roles: ['student'] },
        { label: 'Profile', route: '/home/me/preferences', icon: 'Settings', roles: ['student'] },
      ],
    },
    {
      title: 'Teach',
      space: 'teach',
      items: [
        { label: 'Teaching Overview', route: '/teach', icon: 'Home', roles: ['teacher', 'instructor'], exact: true },
        { label: 'Classes', route: '/teach/classes', icon: 'Users', roles: ['teacher', 'instructor'] },
        { label: 'Assignments', route: '/teach/assignments', icon: 'ClipboardList', roles: ['teacher', 'instructor'] },
        { label: 'Curriculum', route: '/teach/curriculum', icon: 'BookOpen', roles: ['teacher', 'instructor'] },
        { label: 'Learning Paths', route: '/home/programs', icon: 'ClipboardList', roles: ['teacher', 'instructor'] },
        { label: 'Learner Progress', route: '/teach', icon: 'SlidersHorizontal', roles: ['teacher', 'instructor'] },
        { label: 'Settings', route: '/teach/settings', icon: 'Settings', roles: ['teacher', 'instructor'] },
      ],
    },
    {
      title: 'Studio',
      space: 'studio',
      items: [
        { label: 'Studio Overview', route: '/studio', icon: 'Home', roles: ['content_admin'], exact: true },
        { label: 'Projects', route: '/studio/projects', icon: 'ClipboardList', permission: 'nav:projects', roles: ['content_admin'] },
        { label: 'Content', route: '/studio/content', icon: 'BookOpen', permission: 'nav:products', roles: ['content_admin'] },
        { label: 'Courses', route: '/studio/courses', icon: 'Book', permission: 'nav:products', roles: ['content_admin'] },
        { label: 'Programs and Paths', route: '/studio/programs', icon: 'ClipboardList', permission: 'nav:products', roles: ['content_admin'] },
        { label: 'Sources', route: '/studio/sources', icon: 'FileText', permission: 'nav:knowledge-sources', roles: ['content_admin'] },
        { label: 'Content Drafts', route: '/studio/drafts', icon: 'FileText', permission: 'nav:product-studio', roles: ['content_admin'] },
        { label: 'Review', route: '/studio/review', icon: 'ClipboardList', permission: 'nav:review-center', roles: ['content_admin'] },
        { label: 'Publishing', route: '/studio/publishing', icon: 'SlidersHorizontal', permission: 'nav:products', roles: ['content_admin'] },
      ],
    },
    {
      title: 'Organization',
      space: 'organization',
      items: [
        { label: 'Organization Overview', route: '/organization', icon: 'Home', roles: ['org_admin'], exact: true },
        { label: 'Members', route: '/organization/members', icon: 'Users', roles: ['org_admin'] },
        { label: 'Teachers', route: '/organization/teachers', icon: 'Users', roles: ['org_admin'] },
        { label: 'Students', route: '/organization/students', icon: 'Users', roles: ['org_admin'] },
        { label: 'Invitations', route: '/organization/invitations', icon: 'Users', roles: ['org_admin'] },
        { label: 'Classes', route: '/organization/sections', icon: 'BookOpen', roles: ['org_admin'] },
        { label: 'Course Availability', route: '/organization/courses', icon: 'Book', roles: ['org_admin'] },
        { label: 'Settings', route: '/organization/settings', icon: 'Settings', roles: ['org_admin'] },
      ],
    },
    {
      title: 'Admin',
      space: 'admin',
      items: [
        { label: 'Admin Overview', route: '/admin', icon: 'Home', roles: ['admin', 'super_admin'], exact: true },
        { label: 'Users', route: '/admin/users', icon: 'Users', permission: 'nav:admin-users', roles: ['admin'] },
        { label: 'Organizations', route: '/admin/organizations', icon: 'Users', roles: ['admin', 'super_admin'] },
        { label: 'Courses', route: '/admin/courses', icon: 'BookOpen', permission: 'nav:admin-courses', roles: ['admin'] },
        { label: 'Badges', route: '/admin/badges', icon: 'Award', roles: ['admin', 'super_admin'] },
        { label: 'Reports', route: '/admin/reports', icon: 'SlidersHorizontal', permission: 'nav:admin-reports', roles: ['admin'] },
      ],
    },
  ];

  visibleSections(permissions: Set<string>): ShellNavSection[] {
    return this.sections
      .map((section) => ({
        ...section,
        items: section.items.filter((item) => this.itemIsVisible(item, permissions)),
      }))
      .filter((section) => section.items.length > 0);
  }

  getPrimarySpace(permissions: Set<string>, outcome?: BootstrapOutcome): ShellSpaceSummary {
    const roles = this.rolesFromPermissions(permissions);

    if (this.hasRole(roles, ['admin', 'super_admin'])) {
      return {
        name: 'Admin',
        eyebrow: 'EchoEd Admin',
        description: 'Manage people, curriculum oversight, reporting, and platform safeguards.',
        canonicalRoute: '/admin',
      };
    }

    if (this.hasRole(roles, ['org_admin'])) {
      return {
        name: 'Organization',
        eyebrow: 'EchoEd Organization',
        description: 'Manage members, invitations, classes, access, and organization settings.',
        canonicalRoute: '/organization',
      };
    }

    if (this.hasRole(roles, ['content_admin'])) {
      return {
        name: 'Studio',
        eyebrow: 'EchoEd Studio',
        description: 'Prepare, review, and steward learning content for your community.',
        canonicalRoute: '/studio',
      };
    }

    if (this.hasRole(roles, ['teacher', 'instructor'])) {
      return {
        name: 'Teach',
        eyebrow: 'EchoEd Teach',
        description: 'Guide classes, curriculum, assignments, and learner support.',
        canonicalRoute: '/home',
      };
    }

    if (this.hasRole(roles, ['student']) || outcome?.status === 'ready') {
      return {
        name: 'Learn',
        eyebrow: 'EchoEd Learn',
        description: 'Resume learning, follow courses, and track progress.',
        canonicalRoute: '/learn',
      };
    }

    return {
      name: 'EchoEd',
      eyebrow: 'EchoEd',
      description: 'Continue your learning community work.',
      canonicalRoute: '/home',
    };
  }

  canonicalRouteForCurrentUser(): string {
    return this.getPrimarySpace(
      this.permissionsService.getCurrentPermissions(),
      this.permissionsService.getCurrentOutcome(),
    ).canonicalRoute;
  }

  rolesFromPermissions(permissions: Set<string>): string[] {
    return ROLE_PRIORITY.filter((role) => permissions.has(`role:${role}`));
  }

  private itemIsVisible(item: ShellNavItem, permissions: Set<string>): boolean {
    const roleAllowed = !item.roles?.length || item.roles.some((role) => permissions.has(`role:${role}`));
    const permissionAllowed = !item.permission || permissions.has(item.permission);
    return roleAllowed && permissionAllowed;
  }

  private hasRole(roles: string[], allowed: string[]): boolean {
    return allowed.some((role) => roles.includes(role));
  }
}
