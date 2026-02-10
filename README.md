# EchoEd
[![CI](https://github.com/YOUR_USERNAME/EchoEd/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/EchoEd/actions/workflows/ci.yml) [![Docker](https://github.com/YOUR_USERNAME/EchoEd/actions/workflows/docker.yml/badge.svg)](https://github.com/YOUR_USERNAME/EchoEd/actions/workflows/docker.yml)

**Echoing the Past, Educating the Future**

EchoEd is an interactive web and mobile platform designed to educate all ages on African and African-American history. Featuring engaging lessons, gamification, and an interactive timeline, EchoEd makes learning history immersive and accessible.

---

## 🚀 Features
- **Curated Lessons & Modules** – Short, digestible lessons with media-rich content.
- **Interactive Timeline** – Explore key historical events dynamically.
- **Gamification & Achievements** – Earn badges, track progress, and compete on leaderboards.
- **Community Forum** – Discuss historical topics and engage in "Ask a Historian" sessions.
- **Oral Storytelling** – Audio narratives to preserve historical traditions.
- **Future AR Features** – Experience history through augmented reality.

---

## 🛠 Tech Stack
### **Frontend:**
- **Framework:** Angular
- **Styling:** TailwindCSS / Material UI

### **Backend:**
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **Authentication:** JWT-based authentication

### **Infrastructure:**
- **Hosting:** AWS / DigitalOcean
- **CI/CD:** GitHub Actions (Planned)

---

## 📦 Project Structure
```bash
EchoEd/
│── frontend/        # Angular Web & Mobile UI
│── backend/         # FastAPI API & Database
│── docs/            # Pitch Deck, Branding Assets, UI Mockups
│   └── design-guidelines.md  # UI inspiration notes
│── assets/          # Logos, Icons, Images
│── tests/           # Automated tests
│── README.md        # Overview & instructions
│── .gitignore       # Ignore unnecessary files
│── LICENSE          # Open-source license
```

---

## 🔧 Installation & Setup
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/YOUR_USERNAME/EchoEd.git
cd EchoEd
```

### **2️⃣ Backend Setup (FastAPI)**
```sh
cd backend
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Seed demo data:
```sh
python -m app.seed_demo
```

### **3️⃣ Frontend Setup (Angular)**
```sh
cd frontend
npm install
ng serve
```
The Angular dev server proxies `/api` requests to `http://127.0.0.1:8000` via `frontend/proxy.conf.json`, so keep the backend running locally when working in dev mode.

### **Setting Build Environments**
Angular uses environment files in `frontend/src/environments` to change values during different builds. The default `ng serve` uses `environment.ts`. To build with the production settings from `environment.prod.ts`, run:

```sh
ng build --configuration production
```

You can add more environment files (e.g., `environment.staging.ts`) and reference them with `--configuration <name>` once configured in `angular.json`.

## 🗒️ Environment Variables
The backend loads configuration from a `.env` file using **python-dotenv**. Create a file named `.env` in the project root with values like:

```env
DATABASE_URL=postgresql://echoed_user:your_secure_password@localhost/echoed
STORYBOOK_PATH=./storybook
COLORINGS_PATH=./colorings
BADGES_PATH=./badges
JWT_SECRET=your_jwt_secret
FRONTEND_URL=http://localhost:4200
```

- `DATABASE_URL` – Connection string used by `database.py` to initialize the database.
- `STORYBOOK_PATH` – Folder for uploaded storybook pages. `main.py` exposes it at `/storybook`.
- `COLORINGS_PATH` – Folder for coloring pages served at `/colorings`.
- `BADGES_PATH` – Folder for badge images served at `/badges`.
- `JWT_SECRET` – Secret key used for signing JSON Web Tokens.
- `FRONTEND_URL` – Allowed origin(s) for CORS. Use a comma-separated list for multiple URLs.
- `STORYBOOK_PATH`, `COLORINGS_PATH`, `BADGES_PATH` – File storage locations for uploads.

> **Org Context Header:** Most org-scoped endpoints require `X-Org-Id` to be set by the frontend (handled by the org interceptor).

If any variable is omitted, the application falls back to the example values above.

## 🐳 Docker Compose
1. Create a `.env` file in the project root with the variables above.
2. Build and start the stack:
   ```sh
   docker compose up --build
   ```
   This spins up the FastAPI backend along with PostgreSQL and MinIO.
3. Access the API at [http://localhost:8000/docs](http://localhost:8000/docs).
---

## 🚀 Usage
- **Run Frontend:** Open [http://localhost:4200](http://localhost:4200)
- **Run Backend API:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for API documentation
  - The `/api/start-course` endpoint now returns `400` with `"Course already completed"` if the user tries to start a finished course.

## 🧪 Running Tests

### **Backend**
```sh
cd backend
pytest
```

Generate coverage:
```sh
pytest --cov=app --cov-report=term-missing
```

### **Frontend**
```sh
cd frontend
ng test
```

Generate coverage:
```sh
ng test --code-coverage
```

---

## 🧭 Platform Roles & Core Flows

### **Platform roles**
- `super_admin` – Global platform control, diagnostics, and ops.

### **Organization roles**
- `org_admin` – Manages org settings, invites, and staffing.
- `content_admin` – Authors and publishes courses.
- `teacher` – Manages sections and assignments (in-person or remote).
- `parent` – Monitors student progress and supports learning at home.
- `student` – Consumes courses and completes activities.
- `instructor` – Higher-ed teaching role (remote-first).
- `viewer` – Read-only access for observers/guests.

### **Key flows**
1. **Organization setup** → New users can create an org during registration or complete the onboarding screen after login. Users with only a Personal Org are prompted to create a real org before continuing.
2. **Invitations** → Org admins invite users; accepted invites create memberships.
3. **Course authoring** → Content admins create course containers, draft versions, and publish immutable versions.
4. **Sections** → Teachers create sections linked to a course version and enroll learners.
5. **Learning** → Students enroll, resume progress by unit/lesson/activity, and earn badges.
6. **Assignments & sessions** → Teachers assign units/lessons, start live sessions, and review progress summaries.
---

## 🤝 Contributing
We welcome contributions! To contribute:
1. Fork the repository.
2. Create a new branch (`feature-branch`).
3. Commit your changes and push to your fork.
4. Open a Pull Request (PR).

---

## 📜 License
This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🎨 Design Inspiration
Looking for styling tips? Check out [docs/design-guidelines.md](docs/design-guidelines.md) for notes on giving EchoEd a look similar to popular course platforms like Udemy or Pluralsight.

---

## 📬 Contact & Community
- **Website:** [Coming Soon]
- **Email:** support@echoed.com
- **GitHub Issues:** Report bugs or request features in the [Issues tab](https://github.com/YOUR_USERNAME/EchoEd/issues).
- **Follow Us:** [Twitter](#) | [LinkedIn](#)

---

Let's **Echo the Past & Educate the Future** together! 🌍📚
