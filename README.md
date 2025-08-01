# EchoEd

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
uvicorn main:app --reload
```

### **3️⃣ Frontend Setup (Angular)**
```sh
cd frontend
npm install
ng serve
```

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
```

- `DATABASE_URL` – Connection string used by `database.py` to initialize the database.
- `STORYBOOK_PATH` – Folder for uploaded storybook pages. `main.py` exposes it at `/storybook`.
- `COLORINGS_PATH` – Folder for coloring pages served at `/colorings`.
- `BADGES_PATH` – Folder for badge images served at `/badges`.
- `JWT_SECRET` – Secret key used for signing JSON Web Tokens.

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

