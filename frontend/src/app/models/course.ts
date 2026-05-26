import { Unit } from "./unit";

export interface Course {
    id: string;
    title: string;
    description: string;
    learning_objectives?: string;
    skill_tags?: string[];
    standards_metadata?: Record<string, unknown>;
    /** Optional thumbnail URL for course card */
    thumbnailUrl?: string;
    /** Optional instructor name */
    instructor?: string;
    /** Optional course rating (0-5 scale) */
    rating?: number;
    /** Optional number of ratings */
    ratingCount?: number;
    units?: Unit[];
    created_at: Date;
}
