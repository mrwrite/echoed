// src/app/models/segment-response.model.ts
export interface StartCourseRequest {
  course_id: string;
}

export interface SegmentResponse {
  lesson_id: string;
  status: string;
  unit_progress_id?: string; // Optional, used to track progress in the unit
}
