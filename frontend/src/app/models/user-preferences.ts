export interface UserPreferences {
  locale: string;
  timezone?: string | null;
  theme: string;
  large_text: boolean;
  dyslexia_font: boolean;
  preferred_mode: string;
  reading_level_mode: string;
}
