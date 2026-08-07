# Course Studio Observability

The backend emits `course_studio.<operation>.<result>` at supported API boundaries and increments `echoed_course_studio_operations_total{operation,result}`. Operations include template use/listing, import validation, draft creation, draft save, revision conflict, preview, review submission/transition, duplication, publish attempt, publish blocked, and publish success.

Course/resource identifiers may appear in restricted logs when useful for correlation, but never as metric labels. Course graphs, unit/lesson/activity content, assessment answers, imported document bodies, sources, uploaded files, feedback text, and form payloads are excluded. Existing validation details remain in normal authorized API responses, not diagnostic events.

Angular autosave failure leaves the draft dirty and browser content intact. Unexpected save/publish failures may show the backend request reference and emit only operation, HTTP status, and request ID to the browser console. Revision conflicts and validation failures retain their deliberate workflow messaging without reference clutter.

No version-restore endpoint currently exists; therefore Phase 10 does not invent or instrument one. Duplicate is the supported recovery-style operation. Preview failures that escape domain handling are still observable through normalized HTTP and unexpected-request signals.
