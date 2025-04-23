// role-feature-map.ts
export const RoleFeatureMap: { [feature: string]: string[] } = {
    viewUsers: ['admin'],
    viewStudents: ['admin', 'teacher'],
    editUser: ['admin'],
    viewReports: ['admin'],
    addCourse: ['admin', 'teacher'],
    approveRequest: ['admin'],
  };
  