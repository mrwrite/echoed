# Studio Content Validation

Date: 2026-07-13

## Verified validation

The lesson-governance evaluator identifies concrete missing fields: title; objective or learning objectives; key concepts; hook; content; guided practice; independent practice; assessment; and at least one source with a citation and valid optional HTTP(S) URL.

Course publish-readiness and safe-publish endpoints return explicit blocking issues and warnings, and the V2 review center summarizes their counts. Content administrators can see that summary when the course is organization-visible, but the canonical Studio cannot open a complete authorized lesson editor to resolve it.

V2 create endpoints also validate supported product type, visibility, access model, source type, artifact type, workspace/project relationships, and linked source/product ownership.

## Presentation rules

- Studio shows only API-returned readiness text or concrete form requirements.
- Missing source citation is presented as a factual attention state, not a credibility score.
- API rejection is an error; the frontend does not reclassify it as a warning.
- Review and wrapper status are not treated as proof that lessons are publish-ready.
- No numeric readiness or completeness score is calculated.

## Current limitations

There is no content-admin validation endpoint spanning wrapper, source, asset, curriculum, assessment, and publishing dependencies. Alt-text, rights, file safety, program order, and wrapper-to-runtime coherence cannot be validated comprehensively.
