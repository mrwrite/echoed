export interface Lesson {
    id: string;
    title: string;
    objective: string;
    duration_minutes: number;
    activities: any[]; // List of activities within the lesson
}