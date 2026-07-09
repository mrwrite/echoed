# Contributing to EchoEd

Thank you for considering a contribution. EchoEd is early, open source, and preparing for public community outreach. Contributions are welcome, but asks should stay specific, bounded, and respectful of people's time.

## Ways to Contribute

Useful Phase 1 contributions include:
- Documentation improvements.
- Setup and onboarding fixes.
- Educator or curriculum review.
- Historical accuracy or source review.
- Accessibility review.
- Frontend polish.
- Backend tests.
- Demo reliability improvements.
- Good-first-issue cleanup.

## First Contribution Workflow

1. Read [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
2. Pick a small issue labeled `good first issue`, `documentation`, `accessibility`, `frontend`, `backend`, `testing`, `demo`, or `educator feedback`.
3. Comment on the issue before starting if the scope is unclear.
4. Create a focused branch.
5. Make the smallest change that solves the issue.
6. Run the relevant checks.
7. Open a pull request using the template.

## Local Backend Setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Local Frontend Setup

```powershell
cd frontend
npm install
npm start
```

The frontend runs at `http://localhost:4200`. The backend runs at `http://127.0.0.1:8000`.

## Environment Variables

Create `.env` in the repository root:

```env
DATABASE_URL=postgresql://echoed_user:your_secure_password@localhost/echoed
STORYBOOK_PATH=./storybook
COLORINGS_PATH=./colorings
BADGES_PATH=./badges
JWT_SECRET=your_jwt_secret
FRONTEND_URL=http://localhost:4200
```

Do not commit real secrets.

## Demo Seed Data

To reset deterministic demo data:

```powershell
backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py
```

Use [docs/demo-readiness.md](docs/demo-readiness.md) for operator setup and [docs/public-demo.md](docs/public-demo.md) for public evaluation.

## Testing

Run the checks relevant to your change.

Backend:

```powershell
cd backend
pytest
```

Frontend build:

```powershell
cd frontend
cmd /c npm run build
```

Frontend unit tests:

```powershell
cd frontend
cmd /c .\node_modules\.bin\ng.cmd test --watch=false --browsers=ChromeHeadless
```

Demo smoke:

```powershell
cd frontend
cmd /c .\node_modules\.bin\playwright.cmd test tests/demo/student-flagship-smoke.spec.ts
```

If you cannot run a check, say so in your pull request and explain why.

## Pull Request Expectations

Every pull request should include:
- What changed.
- Why it changed.
- How it was tested.
- Screenshots for visible UI changes.
- Accessibility notes for UI, docs, and content changes.
- Curriculum or community impact notes when relevant.

## Good First Issue Structure

Good starter issues should include:
- Clear problem statement.
- Files or area likely involved.
- Expected outcome.
- Acceptance criteria.
- Suggested validation.
- Whether educator, historical accuracy, accessibility, frontend, backend, docs, or testing review is needed.

Example:

```text
Title: Docs: clarify frontend setup for Windows contributors
Area: documentation
Files: CONTRIBUTING.md, frontend/README.md
Acceptance criteria:
- Windows setup commands are accurate.
- npm PowerShell execution-policy workaround is documented if needed.
- No product code changes.
Validation:
- Read the setup section and confirm commands are copyable.
```

## Educator and Curriculum Feedback

Educator feedback is valuable and should be bounded. Good feedback includes:
- Which demo role or lesson you reviewed.
- Grade or learner context.
- What felt useful.
- What felt unclear, inaccurate, inaccessible, or culturally off.
- Suggested changes or questions.

Use the educator/curriculum feedback issue template when possible.

## Communication Guidelines

- Be specific and respectful.
- Assume people are contributing with limited time.
- Avoid broad requests for unpaid labor.
- Do not claim classroom readiness or historical authority without review.
- Keep feedback focused on the work, not the person.
- Follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Maintainer Capacity

EchoEd currently has no paid budget and no formal contributor program. Review times may vary. The project will prioritize small, clear, mission-aligned contributions.
