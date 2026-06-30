# GymSense AI — Project Specification

## Role
Act as a senior software architect, full-stack engineer, ML engineer, and DevOps engineer building this codebase. Every decision must be production-ready, scalable, and maintainable — this is a **resume/placement-quality** project, not a prototype. When generating code, follow current best practices for the chosen stack (typed Pydantic models, proper error handling, JWT security, async FastAPI routes, React component structure, Dockerized services). When explaining decisions, assume the reader is a capable beginner: briefly state *why* each technology/pattern is used, not just *what* to type.

## Product Overview
GymSense AI is a web app that analyzes wearable sensor data (CSV uploads) from gym sessions and auto-generates exercise summaries, rep counts, workout analytics, and AI-powered fitness recommendations via an LLM.

## Current Status & Constraints
- A pretrained gym-activity classification model already exists, trained on the RecGym dataset. It performs **offline inference** and classifies 12 gym exercises. Treat it as a given artifact (e.g., a `.pt`/`.h5` file + a known input feature schema) — do not redesign the model architecture, only integrate it.
- Real-time wearable streaming is a **future feature** — implement it only as a disabled/dummy UI option ("Start Today's Session"), no real device integration yet.
- The **primary workflow is CSV upload** of a completed wearable session.
- Rep counting uses **signal peak detection** (e.g., SciPy `find_peaks` on smoothed/filtered sensor signal), not the ML model.
- Target deployment: AWS EC2 free tier (backend, Dockerized, behind Nginx + Let's Encrypt SSL via DuckDNS) and Vercel (frontend).

## End-to-End User Workflow
1. Landing page explains GymSense AI and pitches the product (marketing-style, convincing copy).
2. User clicks "Use GymSense" → Login / Register.
3. Registration collects: name, email, password, age, gender, height, weight, fitness goal.
4. Authenticated dashboard shows: "Start Today's Session" (dummy/disabled), "Upload Today's Session" (main feature), recent analytics, workout history.
5. User uploads a session CSV. Backend pipeline: **CSV validation → preprocessing → sliding-window generation → ML inference → prediction smoothing (e.g., majority vote / rolling mode) → exercise segmentation → rep counting (peak detection) → analytics generation.**
6. Results returned: total duration, exercises performed, sets, reps, estimated calories, session summary.
7. User clicks "Analyze My Workout" → current session + historical sessions + user profile are sent to an LLM, which returns: workout analysis, suggestions, progress analysis, consistency analysis, future recommendations.

## Tech Stack
- **Frontend:** React + Vite, Tailwind CSS, Axios, Chart.js
- **Backend:** FastAPI, JWT auth, Pydantic (v2) for schema validation
- **Database:** MongoDB Atlas
- **ML:** PyTorch or TensorFlow (match the existing pretrained model's framework), NumPy, Pandas, SciPy, Scikit-learn
- **Infra:** Docker, Docker Compose (local), AWS EC2 free tier, Nginx reverse proxy, Let's Encrypt SSL, DuckDNS (dynamic DNS for the EC2 IP), Vercel (frontend hosting), GitHub (version control + CI)

## Architectural Expectations
- Backend organized by domain (e.g., `app/auth`, `app/sessions`, `app/ml`, `app/analytics`, `app/llm`), not by technical layer alone — keep routers, services, schemas, and models separated within each domain.
- ML pipeline must be a clean, testable, swappable module (`app/ml/inference.py`, `app/ml/preprocessing.py`, `app/ml/rep_counter.py`, `app/ml/segmentation.py`) — independent of FastAPI request/response concerns so it can later be reused for real-time streaming.
- MongoDB schema design should support: `users` (profile + auth), `sessions` (raw upload metadata + analytics results), `exercise_logs` (per-exercise breakdown within a session) — propose indexes for common queries (user's session history, date ranges).
- JWT auth: access token + refresh token pattern, password hashing with bcrypt/passlib.
- LLM integration should be an isolated service (`app/llm/`) with a clear prompt template that injects current session JSON, summarized historical session data, and user profile — keep prompts and parsing logic testable.
- Frontend organized by feature (`pages/`, `components/`, `api/`, `hooks/`, `context/` for auth state), Axios instance with interceptor for JWT attach/refresh.
- Every feature should be demoable and explainable in an interview: favor clarity and correctness over cleverness.

## Deliverables Expected from Claude Code Throughout
- Folder structure proposals before code generation for any new module.
- Explicit explanation of where each new piece fits in the overall architecture.
- Dockerfiles + docker-compose for local dev, plus deployment notes for EC2/Nginx/DuckDNS/SSL when relevant.
- Tests (pytest for backend, basic component tests for frontend) for core logic, especially the ML pipeline and rep counting.
