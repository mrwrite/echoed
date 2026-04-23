// course-draft.model.ts

export interface LessonDraft {
    id: string;            // Unique ID for internal tracking (UUID or timestamp string)
    title: string;
    objective?: string;
    learning_objectives?: string;
    key_concepts?: string[];
    teacher_notes?: string;
    discussion_questions?: string[];
    hook?: string;
    content?: string;
    guided_practice?: string;
    independent_practice?: string;
    assessment?: string;
    review_status?: string;
    reviewed_by?: string;
    sources?: SourceDraft[];
    order: number;
    duration_minutes?: number;
    activities: ActivityDraft[]; // List of activities within the lesson
    
  }
  
  export interface UnitDraft {
    id: string;            // Unique ID for internal tracking
    title: string;
    content?: string;
    order?: number;       // Optional, for ordering units
    lessons: LessonDraft[];
  }
  
  export interface CourseDraft {
    id?: string;           // Optional, for editing existing courses
    title: string;
    description?: string;
    imageUrl?: string;     // Optional course image
    units: UnitDraft[];
  }

export interface ActivityDraft {
    id: string;
    type: 'video' | 'story' | 'storybook' | 'coloring' | 'song' | 'quiz' | 'reflection' | 'checkpoint' | 'audio' | 'text' | 'discussion';
    title: string;
    content: string; // URL for video, text for story, etc.
    order: number; // Order of the activity within the lesson
    mediaId?: string;
    pages?: StorybookPageDraft[];

  }

export interface StorybookPageDraft {
    id: string;
    imageUrl: string;
    order: number;
}

export interface SourceDraft {
    citation: string;
    url?: string;
}
  
