import { Lesson } from './lesson';

export interface Unit {
    id: string;
    title: string;
    order: number;
    lessons: Lesson[];
}