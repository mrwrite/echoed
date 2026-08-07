# Upload Security Review

| Control | Phase 8 behavior |
| --- | --- |
| Authentication/authorization | coloring/storybook: admin, super admin, teacher, instructor, content admin; badge: admin/super admin |
| Rate limiting | authenticated user key, `upload` policy |
| Size | streamed 5 MiB maximum; partial file removed on failure |
| Format | PNG, JPEG, GIF, WebP only; suffix, claimed MIME, magic structure, dimensions, maximum side (12,000), and maximum pixels (40M) checked |
| SVG/active content | rejected |
| Filename/path | client path is never used for storage; UUID filename plus validated suffix stays in configured directory |
| Completion/overwrite | random name and `.part` atomic replacement; partial cleanup; practical collision resistance |
| Accessibility metadata | binary endpoint returns only file URL; alt text/instructions remain separate lesson/activity data |
| Public access | existing `/storybook`, `/colorings`, `/badges` static paths remain public for compatibility and receive application `nosniff` headers |
| Replace/delete/ownership | no replacement/delete upload endpoint exists; therefore unsupported and disabled |

The server does not trust extension or MIME alone. Rejections emit metadata-only security events. Tests cover unauthorized roles, oversized bodies, MIME mismatch, signature mismatch, path-like filenames, safe generated names, and rate limiting.

Residual risks: standard-library structural checks are not full decoding; metadata is not stripped; there is no malware scanning, quarantine, private per-org delivery, retention cleanup, or object-store isolation. Those belong to the future asset-management/storage change, not this phase.
