export interface Activity {
    type: string; // Type of activity (e.g., "quiz", "video", "discussion")
    description: string; // Description of the activity
    duration_minutes?: number; // Optional duration for the activity
}

export interface Lesson {
    id: string;
    title: string;
    objective: string;
    duration_minutes: number;
    activities: Activity[]; // List of activities within the lesson
}