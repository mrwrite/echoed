from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.schemas import CourseAuthoringDraftRequest


@dataclass(frozen=True)
class ExchangeValidationIssue:
    severity: str
    path: str
    code: str
    message: str


class CourseExchangeAdapter(Protocol):
    format_id: str

    def validate_import(self, payload: dict) -> list[ExchangeValidationIssue]: ...
    def to_authoring_draft(self, payload: dict) -> CourseAuthoringDraftRequest: ...
    def export(self, payload: dict) -> dict: ...


class EchoedJsonAdapter:
    """Lossless first-release exchange format; cartridge/QTI adapters plug in here later."""

    format_id = "echoed-json-v1"

    def validate_import(self, payload: dict) -> list[ExchangeValidationIssue]:
        issues: list[ExchangeValidationIssue] = []
        if payload.get("format") != self.format_id:
            issues.append(ExchangeValidationIssue("blocking", "format", "unsupported_format", "Only echoed-json-v1 is supported in this release."))
        course = payload.get("course")
        if not isinstance(course, dict):
            issues.append(ExchangeValidationIssue("blocking", "course", "missing_course", "The exchange document must contain a course object."))
            return issues
        supported = set(CourseAuthoringDraftRequest.model_fields)
        for field in sorted(set(course) - supported - {"id", "organization_id", "created_by", "revision_status", "revision_metadata", "updated_at", "current_version_id", "assessment_ids", "capabilities"}):
            issues.append(ExchangeValidationIssue("warning", f"course.{field}", "unsupported_construct", f"The field '{field}' will not be imported."))
        try:
            CourseAuthoringDraftRequest.model_validate({key: value for key, value in course.items() if key in supported})
        except Exception as exc:
            issues.append(ExchangeValidationIssue("blocking", "course", "invalid_course_graph", str(exc)))
        return issues

    def to_authoring_draft(self, payload: dict) -> CourseAuthoringDraftRequest:
        supported = set(CourseAuthoringDraftRequest.model_fields)
        return CourseAuthoringDraftRequest.model_validate({key: value for key, value in payload["course"].items() if key in supported})

    def export(self, payload: dict) -> dict:
        return {"format": self.format_id, "course": payload}


echoed_json_adapter = EchoedJsonAdapter()
