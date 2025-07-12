export interface Activity {
    id: string;
    type: string;
    title: string;
    content: string;
    order?: number;
}

export interface Lesson {
    id: string;
    title: string;
    objective: string;
    duration_minutes: number;
    activities: Activity[]; // List of activities within the lesson
}