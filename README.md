# EchoEd

[![CI](https://github.com/mrwrite/EchoEd/actions/workflows/ci.yml/badge.svg)](https://github.com/mrwrite/EchoEd/actions/workflows/ci.yml) [![Docker](https://github.com/mrwrite/EchoEd/actions/workflows/docker.yml/badge.svg)](https://github.com/mrwrite/EchoEd/actions/workflows/docker.yml)

EchoEd is an open-source education platform centered on African and African-American history. It is being prepared for public community review and contribution from educators, developers, students, homeschool leaders, HBCU communities, and community learning organizers across the United States, Africa, and the Caribbean.

Current public app: https://echoed-theta.vercel.app/  
Repository: https://github.com/mrwrite/echoed  
License: [MIT](LICENSE)

## Current Status

EchoEd is early and pre-community-launch.

- Working K-5 demo exists with student, teacher, and admin experiences.
- Demo access uses shared demo-only credentials.
- The project has no current public users, contributors, stars, advisors, or community traction.
- Phase 1 focuses on trust, documentation, contributor onboarding, and public demo readiness before broad outreach begins.

Do not enter personal, student, school, or production data into the demo.

## Mission

EchoEd exists to make culturally grounded Black history learning experiences easier to explore, teach, review, and improve in public. The project aims to combine rigorous historical learning, accessible product design, and open-source community ownership.

## Who This Is For

### Educators

EchoEd needs classroom judgment before it needs scale. Educators can help by reviewing demo flows, lesson tone, age fit, source needs, discussion prompts, and classroom usefulness.

Start here:
- Try the [public demo guide](docs/public-demo.md).
- File educator or curriculum feedback using the GitHub issue templates.
- Read the [community trust guide](docs/community-trust.md) for review expectations and recognition.

### Developers

EchoEd is an Angular and FastAPI application. Developers can help with frontend polish, accessibility, backend tests, demo reliability, documentation, curriculum tooling, and contributor onboarding.

Start here:
- Read [CONTRIBUTING.md](CONTRIBUTING.md).
- Review [ARCHITECTURE.md](ARCHITECTURE.md).
- Look for issues labeled `good first issue`, `help wanted`, `documentation`, `frontend`, `backend`, `testing`, `accessibility`, or `demo`.

### Community Organizers

Community organizers can help connect EchoEd with Black educator networks, homeschool groups, HBCU programs, Black developer groups, and Africa or Caribbean education technology communities.

Start here:
- Review [docs/outreach-readiness.md](docs/outreach-readiness.md).
- Share bounded feedback or introductions through GitHub issues or `support@echoed.com`.

## Public Demo

The live app is available at https://echoed-theta.vercel.app/.

Use the demo only for evaluation. Demo credentials and walkthrough steps are documented in [docs/public-demo.md](docs/public-demo.md). The credentials are shared, demo-only, resettable, and not appropriate for real learner data.

## Project Structure

```text
backend/      FastAPI app, SQLAlchemy models, Alembic migrations, pytest tests
frontend/     Angular app, Tailwind styling, Playwright demo smoke tests
docs/         Demo, outreach, and project guidance
openspec/     Spec-driven change workflow
curriculum/   Seed curriculum and package material
```

For a deeper overview, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Local Development

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm start
```

The frontend dev server runs at `http://localhost:4200` and proxies API calls to `http://127.0.0.1:8000` through `frontend/proxy.conf.json`.

### Environment

Create a `.env` file in the repository root for backend settings:

```env
DATABASE_URL=postgresql://echoed_user:your_secure_password@localhost/echoed
STORYBOOK_PATH=./storybook
COLORINGS_PATH=./colorings
BADGES_PATH=./badges
JWT_SECRET=your_jwt_secret
FRONTEND_URL=http://localhost:4200
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full setup, seed, and test guidance.

## Demo Data

To reset deterministic demo users, content, and learner states:

```powershell
backend\venv\Scripts\python.exe backend\scripts\reseed_demo.py
```

Internal operator details live in [docs/demo-readiness.md](docs/demo-readiness.md). Public-facing demo instructions live in [docs/public-demo.md](docs/public-demo.md).

## Testing

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

Frontend tests:

```powershell
cd frontend
cmd /c .\node_modules\.bin\ng.cmd test --watch=false --browsers=ChromeHeadless
```

Student demo smoke test:

```powershell
cd frontend
cmd /c .\node_modules\.bin\playwright.cmd test tests/demo/student-flagship-smoke.spec.ts
```

## Contributing

EchoEd welcomes bounded, respectful contributions. Because this project is early and has no paid budget, contribution requests should be specific and transparent.

Read:
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
- [ROADMAP.md](ROADMAP.md)
- [docs/community-trust.md](docs/community-trust.md)

## Roadmap

The current priority is Phase 1 public open-source readiness. See [ROADMAP.md](ROADMAP.md) for staged priorities.

## Contact

- General community contact: support@echoed.com
- Security reports: see [SECURITY.md](SECURITY.md)
- Bugs, feedback, and contribution ideas: use GitHub issues

## License

EchoEd is licensed under the [MIT License](LICENSE). Copyright 2025 Anthony Wright.
