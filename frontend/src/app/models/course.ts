import { Unit } from "./unit";

export interface Course {
    id: string;
    title: string;
    description: string;
    units: Unit[];
    created_at: Date;
}