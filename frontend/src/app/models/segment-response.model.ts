// src/app/models/segment-response.model.ts
export interface StartCourseRequest {
  course_id: string;
}

export interface SegmentResponse {
  lesson_id: string;
  status: string;
}
