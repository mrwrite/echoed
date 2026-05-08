// src/app/models/segment-response.model.ts
export interface StartCourseRequest {
  course_id: string;
}

export type GovernedDeliveryState =
  | 'governed_available'
  | 'governed_unavailable'
  | 'pending_review'
  | 'no_approved_content'
  | 'empty_course'
  | 'empty_unit'
  | 'completed';

export interface SegmentResponse {
  lesson_id?: string;
  status?: string;
  unit_progress_id?: string; // Optional, used to track progress in the unit
  delivery_state: GovernedDeliveryState;
  detail?: string;
}

export interface CompleteSegmentResponse {
  message: string;
  segment_id: string;
  next_segment: SegmentResponse;
}
