# Studio Asset and Upload Data Contract

Date: 2026-07-13

## Current uploads

| Endpoint | Purpose | Authorized roles | Response |
| --- | --- | --- | --- |
| `POST /api/upload/coloring` | Coloring image | admin, teacher | Public `file_path` |
| `POST /api/upload/storybook` | Storybook page image | admin, teacher | Public `file_path` |
| `POST /api/upload/badge` | Badge image | admin | Public `file_path` |

The endpoints generate UUID filenames and copy bytes to configured directories. They do not expose a content-admin asset library, search, metadata, alt text, caption, rights/license, usage lookup, replacement, deletion, documented accepted types, documented size limits, or upload progress.

## Studio decision

Canonical Studio has no Assets navigation or upload control. A `KnowledgeSource` may record `source_type: upload`, but this is metadata only and does not upload a file.

## Required future contract

A future asset capability must define MIME allowlists, size limits, malware/content handling, organization scope, alt text, rights notes, usage relationships, safe replacement/deletion semantics, and response errors before learner-facing uploads can be exposed to content administrators.
