# Council of Minds

A monorepo web application structured into independent, deployable backend and frontend units.

## Project Structure

```text
council-of-minds/
├── backend/          # FastAPI Python backend
│   ├── app/          # Application source code (layered architecture)
│   ├── tests/        # Pytest automated test suite
│   ├── requirements.txt
│   └── pyproject.toml
└── frontend/         # React + Vite + JavaScript frontend
    ├── src/          # Frontend source code
    └── package.json
```

---

## Backend Setup & Running

The backend is built with **FastAPI** and uses **Pydantic Settings** for environment-based configuration.

### 1. Python Virtual Environment Creation & Activation

We recommend using Python 3.10+ and creating an isolated virtual environment (`venv`) inside the `backend/` directory.

#### On Windows (PowerShell / Command Prompt):
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

#### On macOS / Linux:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
With your virtual environment activated:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configuration variables supported (can be prefixed with `BACKEND_` or plain):
- `BACKEND_ENVIRONMENT`: Application environment (e.g., `development`, `production`)
- `BACKEND_APP_PORT`: Port to bind the server (default: `8000`)
- `BACKEND_ALLOWED_ORIGINS`: Comma-separated list or JSON array of CORS origins
- `BACKEND_LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `BACKEND_VERSION`: Current application version

### 4. Running the Backend Server
To boot the FastAPI server with hot-reloading:
```bash
uvicorn app.main:app --reload --port 8000
```
The server will be accessible at `http://localhost:8000`.
- Health check endpoint: `http://localhost:8000/health`
- API Documentation: `http://localhost:8000/docs`

### 5. Running Backend Tests & Linting
To run the automated test suite:
```bash
pytest
```
To check code formatting and linting:
```bash
ruff check .
black --check .
```

---

## Frontend Setup & Running

The frontend is built with **React**, **Vite** (Plain JavaScript), **Tailwind CSS**, and modern state/data management tools (**Zustand**, **React Query**, **Axios**, **React Router**).

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Configuration variables supported:
- `VITE_API_BASE_URL`: Base URL for backend API requests (default: `http://localhost:8000`)
- `VITE_APP_NAME`: Name displayed in the UI

### 3. Running the Frontend Development Server
```bash
npm run dev
```
The application will be accessible at `http://localhost:5173`.

### 4. Linting & Formatting
To check code quality and styling:
```bash
npm run lint
```
