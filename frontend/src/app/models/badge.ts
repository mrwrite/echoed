export interface Badge {
  id: string;
  title: string;
  description?: string;
  image_url?: string;
  created_at: Date;
  updated_at: Date;
}

export interface BadgeCreate {
  title: string;
  description?: string;
  image_url?: string;
}

export interface StudentBadge {
  id: string;
  student_id: string;
  badge_id: string;
  awarded_at: Date;
  badge?: Badge;
}
