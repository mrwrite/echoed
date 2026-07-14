# Studio Source Data Contract

Date: 2026-07-13

## V2 source wrapper

`KnowledgeSource` provides `id`, `workspace_id`, `project_id`, optional legacy `source_id`, `title`, `source_type`, optional `uri`, optional `citation`, optional `content_hash`, `status`, metadata, and timestamps.

Supported types are `repository`, `document`, `pdf`, `url`, `transcript`, `upload`, `manual_note`, and `lesson_source`.

## Legacy lesson source

`Source` provides `id`, `lesson_id`, `citation`, optional URL, and creation timestamp. It has no independent CRUD route. Lesson readiness requires at least one non-empty citation; an optional URL must be valid HTTP(S).

## Supported Studio operations

- List/search/filter organization-scoped knowledge-source wrappers.
- Create a source wrapper inside an authorized project.
- Record title, type, URI/reference, and citation.
- Show whether citation text is recorded.
- Associate a source wrapper when creating an artifact in the same project.

## Unsupported operations

There is no source detail, edit, delete, usage-lookup, duplicate-detection, rights/license, author, publisher, date, primary/secondary classification, or file-preview API. Studio does not invent those fields, claim a source is unused, or assign trust/reliability scores.

Removing an artifact association is also unsupported. No delete/unlink control is shown.
