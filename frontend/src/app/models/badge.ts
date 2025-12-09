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
