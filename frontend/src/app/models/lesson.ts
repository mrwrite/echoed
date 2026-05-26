export interface Activity {
    id: string;
    type: string;
    title: string;
    content: string;
    order?: number;
    pages?: StorybookPage[];
}

export interface StorybookPage {
    id: string;
    image_url: string;
    order?: number;
}

export interface Source {
    id: string;
    citation: string;
    url?: string;
    created_at?: string;
}

export interface Lesson {
    id: string;
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
    review_status?: 'draft' | 'reviewed' | 'approved' | string;
    reviewed_by?: string;
    duration_minutes?: number;
    sources?: Source[];
    is_ready_for_approval?: boolean;
    missing_readiness_fields?: string[];
    activities: Activity[]; // List of activities within the lesson
}
