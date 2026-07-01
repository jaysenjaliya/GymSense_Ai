# GymSense AI — Project Specification

## Role
Act as a senior software architect, full-stack engineer, ML engineer, and DevOps engineer building this codebase. Every decision must be production-ready, scalable, and maintainable — this is a **resume/placement-quality** project, not a prototype. When generating code, follow current best practices for the chosen stack (typed Pydantic v2 models, proper error handling, JWT security, async FastAPI routes, React component structure, Dockerized services). When explaining decisions, assume the reader is a capable beginner: briefly state *why* each technology/pattern is used, not just *what* to type.

---

## Product Overview
GymSense AI is a web app that analyzes wearable sensor data (CSV uploads) from gym sessions and auto-generates exercise summaries, rep counts, workout analytics, and AI-powered fitness recommendations via an LLM (Google Gemini).

---

## Current Asset Status

| Asset | Status |
|---|---|
| Hybrid CNN + PostFusion model (12 classes, PyTorch) | Done in notebook |
| LOUO training/evaluation pipeline | Done in notebook — do NOT reuse directly in production |
| `subject-10.pt` (wrist-only weights) | Must be placed at `backend/ml/weights/wrist/subject-10.pt` |
| `sample_session.csv` (~40,280 rows, wrist position) | Provided — use for all smoke tests |
| Full-stack application | 0% built |

---

## Pretrained Model — Critical Details (Do Not Change)

- **Architecture:** `PostFusion` using `getModel()` — extracted from notebook as-is into `backend/ml/model.py`
- **Input shape:** `(N, 1, 80, 7)` — 80-sample sliding windows, 7 channels, **no scaling applied**
- **7 channels (exact order):** `A_x`, `A_y`, `A_z`, `G_x`, `G_y`, `G_z`, `C_1`
- **12 output classes (exact order):** `Adductor`, `ArmCurl`, `BenchPress`, `LegCurl`, `LegPress`, `Null`, `Riding`, `RopeSkipping`, `Running`, `Squat`, `StairClimber`, `Walking`
- **Inference pattern:** load weights → `model.eval()` → forward pass → `argmax` on logits
- **Sampling rate:** ~20 Hz → 80 samples = 4 seconds per window
- **Scope:** v1 supports **wrist CSVs only** (single model, no position selection)
- **Notebook warning:** `load_data_Gym()` uses LOUO/fold logic for research evaluation — strip this entirely when porting to production `preprocess.py`
- **Model loading:** Load weights **once at FastAPI startup** (not per-request) for performance

---

## User CSV Format

**Required columns (all must be present and numeric):**
`A_x`, `A_y`, `A_z`, `G_x`, `G_y`, `G_z`, `C_1`

**Optional metadata columns (ignored by model):**
`Workout`, `Subject`, `Position`, `Session`, timestamps

**Validation rules:**
- All 7 sensor columns present and numeric
- Minimum 800 rows for a meaningful session (80 rows = absolute floor for one window)
- No NaN or inf values
- If timestamp column present: must be monotonically increasing

**Sample file:** `sample_session.csv` — columns: `Subject`, `Position`, `Session`, `A_x`, `A_y`, `A_z`, `G_x`, `G_y`, `G_z`, `C_1`, `Workout` — exercises present: `Null`, `Squat`, `ArmCurl`, `BenchPress` (and others)

---

## End-to-End User Workflow

1. Landing page — marketing-style, convincing copy explaining GymSense AI; includes "Download sample session" link for users without wearable data.
2. User clicks "Use GymSense" → Login / Register.
3. Registration collects: name, email, password, age, gender (enum: `male/female/other`), height (cm), weight (kg), fitness goal (enum: `fat_loss/muscle_gain/endurance/general_fitness`). Store weight in kg and height in cm always — convert in frontend if needed.
4. Dashboard: "Start Today's Session" (disabled dummy), "Upload Today's Session" (main feature), recent analytics cards, workout history list. "Try with sample data" quick-action downloads sample CSV.
5. User uploads CSV. Backend pipeline (synchronous for v1 — no task queue):
   **CSV validation → preprocessing (windowing) → ML inference (PostFusion) → prediction smoothing (rolling majority vote, filter Null) → exercise segmentation → rep counting (SciPy find_peaks) → set estimation (15s rest gap threshold) → calorie estimation (MET formula) → analytics aggregation → store to MongoDB → return summary**
6. Results page: total duration, exercises performed, sets, reps per set, estimated calories, session summary.
7. "Analyze My Workout" → current session JSON + summarized historical sessions + user profile → Gemini API → structured response: workout analysis, suggestions, progress analysis, consistency analysis, future recommendations. Cache response in `ai_analyses` collection; do not re-call Gemini unless user explicitly requests refresh.

---

## ML Pipeline — Module Responsibilities

| Module | Responsibility |
|---|---|
| `backend/ml/model.py` | `PostFusion`, `ConvBlock`, `MHABlock`, `DIBlock`, `getModel()` — architecture only, copied from notebook |
| `backend/ml/preprocess.py` | Read user CSV → validate columns → extract 7 channels → slice into `(N, 1, 80, 7)` windows (stride 80, no overlap for v1) → return tensor |
| `backend/ml/inference.py` | Load `subject-10.pt` at startup, batch predict on windows, return list of class indices |
| `backend/ml/postprocess.py` | Map indices → label names; merge consecutive identical labels into segments `{exercise, start_idx, end_idx, window_count}`; filter out `Null` segments; compute duration per segment = `window_count × 4s` |
| `backend/ml/rep_counter.py` | For each segment: extract raw IMU slice → pick axis with highest variance → apply Savitzky-Golay smoothing → `scipy.signal.find_peaks` with tuned `distance`/`prominence` → cluster peaks separated by >15s into sets → return `{reps_per_set: [...], total_reps, total_sets}` |
| `backend/ml/calories.py` | MET-based formula: `calories = MET × weight_kg × duration_hours`. MET values: Squat=5.0, ArmCurl=3.5, BenchPress=3.8, LegCurl=3.5, LegPress=3.5, Running=9.8, Walking=3.5, Adductor=3.5, Riding=6.0, RopeSkipping=10.0, StairClimber=8.0. Label all calorie values "estimated" in UI. |
| `backend/ml/validator.py` | Standalone CSV validation — column check, row count, NaN/inf check, range sanity check |

**CLI smoke test (must work):** `python -m ml.inference --csv backend/assets/sample_session.csv` → prints JSON with segments, reps, sets, calories.

---

## Backend API Endpoints

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/register` | No | Registration |
| POST | `/auth/login` | No | Returns access + refresh tokens |
| POST | `/auth/refresh` | No | New access token from refresh token |
| GET | `/auth/me` | Yes | Current user profile |
| POST | `/sessions/upload` | Yes | CSV upload → full pipeline → store + return summary |
| GET | `/sessions` | Yes | Paginated session history list |
| GET | `/sessions/{id}` | Yes | Session detail with exercise logs |
| POST | `/sessions/{id}/analyze` | Yes | Trigger Gemini analysis (checks cache first) |
| GET | `/analytics/summary` | Yes | Aggregated stats for dashboard cards |
| GET | `/samples/session` | No | Download `sample_session.csv` (no auth required) |

---

## Database Schema

**`users` collection** — indexes: `email` (unique)
Fields: `_id`, `name`, `email`, `hashed_password`, `age`, `gender` (enum), `height_cm`, `weight_kg`, `fitness_goal` (enum), `created_at`, `updated_at`

**`sessions` collection** — indexes: `user_id`, `created_at` (descending)
Fields: `_id`, `user_id`, `status` (enum: `pending/processing/completed/failed`), `duration_seconds`, `total_exercises`, `total_sets`, `total_reps`, `total_calories_estimated`, `row_count`, `created_at`

**`exercise_logs` collection** — indexes: `session_id`, `user_id + exercise_name` (for cross-session exercise queries)
Fields: `_id`, `session_id`, `user_id`, `exercise_name`, `set_number`, `reps`, `duration_seconds`, `calories_estimated`, `start_row_idx`, `end_row_idx`

**`ai_analyses` collection** — index: `session_id` (unique)
Fields: `_id`, `session_id`, `user_id`, `analysis`, `suggestions`, `progress`, `consistency`, `recommendations`, `created_at`, `model_used`

**Authorization rule (never skip):** On every `sessions` or `exercise_logs` or `ai_analyses` query, always filter by both `session_id` AND `user_id` from the JWT — never trust a client-supplied user ID.

---

## Auth Design

- **Tokens:** Short-lived access token (30 min) + long-lived refresh token (7 days)
- **Refresh token strategy:** DB-whitelisted (store hashed refresh token in user document) — more production-realistic than pure stateless, allows logout/revocation
- **Password hashing:** passlib + bcrypt
- **`get_current_user` dependency:** decodes JWT from `Authorization: Bearer` header, fetches user from MongoDB, raises HTTP 401 if invalid — imported by every protected router
- **No email verification for v1** — auto-login after registration

---

## LLM Integration (Gemini)

- **Service location:** `backend/app/llm/` — completely isolated from other domains
- **Prompt inputs:** user profile (age, gender, height_cm, weight_kg, fitness_goal) + current session breakdown (exercise name, sets, reps per set, duration, calories) + last 5 historical sessions (aggregated stats only — do not dump raw exercise_logs, summarize to avoid token waste)
- **Output structure:** Parse Gemini response into 5 named sections: `analysis`, `suggestions`, `progress`, `consistency`, `recommendations` — return as structured JSON so frontend renders each section independently
- **Caching:** Check `ai_analyses` collection for existing analysis before calling Gemini. Only call Gemini if no cached result exists or user explicitly requests refresh via a `?refresh=true` query param
- **API key:** `GEMINI_API_KEY` from `.env` — never hardcode

---

## Frontend Pages

| Page | Route | Purpose |
|---|---|---|
| Landing | `/` | Hero, features, how-it-works, "Download sample session" link, CTA to register |
| Login | `/login` | Email + password |
| Register | `/register` | All profile fields with validation |
| Dashboard | `/dashboard` | Stats cards, quick actions, recent sessions, "Try with sample data" |
| Upload | `/upload` | CSV drag-drop, validation errors, progress state, "Download sample CSV" helper |
| Session Summary | `/sessions/:id` | Exercise breakdown, rep counts, calories, "Analyze My Workout" CTA |
| AI Analysis | `/sessions/:id/analysis` | Rendered Gemini output in 5 sections |
| Analytics | `/analytics` | Chart.js line/bar/pie charts for progress over time |
| History | `/history` | Paginated session list |

**Frontend architecture rules:**
- Axios instance in `src/api/client.js` with request interceptor (attach JWT) and response interceptor (auto-refresh on 401)
- Auth state in React Context (`src/context/AuthContext.jsx`) — wraps entire app
- Custom hooks in `src/hooks/` for data fetching (e.g., `useSessions`, `useAnalytics`)
- Never store raw JWT in localStorage in production-facing discussions — use httpOnly cookie or at minimum acknowledge the XSS trade-off in README

---

## Sample CSV Download (Public Feature)

- **Backend:** `GET /samples/session` — returns `backend/assets/sample_session.csv` with `Content-Disposition: attachment` header — **no auth required**
- **Frontend static:** Also bundle at `frontend/public/samples/sample_session.csv` for direct Vercel CDN download (works even if API is down)
- **UX copy:** "Demo wrist sensor data in RecGym format — upload this to see exercise recognition, rep counts, and AI analysis"
- **Placement:** Landing page "How It Works" section + Upload page secondary action + Dashboard quick action

---

## Repository Structure

```
GymSense_AI/
├── CLAUDE.md
├── sample_session.csv          # Source of truth demo file
├── Hybrid_CNN_PyTorch.ipynb    # Research reference only — do not import from here
├── frontend/
│   ├── public/samples/sample_session.csv
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── api/
│       ├── hooks/
│       └── context/
├── backend/
│   ├── assets/sample_session.csv
│   ├── ml/
│   │   ├── model.py
│   │   ├── preprocess.py
│   │   ├── inference.py
│   │   ├── postprocess.py
│   │   ├── rep_counter.py
│   │   ├── calories.py
│   │   ├── validator.py
│   │   └── weights/wrist/subject-10.pt
│   ├── app/
│   │   ├── main.py
│   │   ├── core/            # config.py, database.py, security.py
│   │   ├── auth/            # routes.py, service.py, schemas.py, dependencies.py
│   │   ├── sessions/        # routes.py, service.py, schemas.py
│   │   ├── analytics/       # routes.py, service.py
│   │   └── llm/             # gemini_service.py, prompt_builder.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── nginx/nginx.conf
```

---

## Environment Variables (`.env` — never commit; commit `.env.example`)

```
MONGODB_URI=
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GEMINI_API_KEY=
MODEL_PATH=
```

---

## Build Phase Sequence

1. **Auth + DB foundation** — MongoDB connection (Motor async), JWT auth, register/login/refresh/me endpoints, user schema with all profile fields. Validate with curl before proceeding.
2. **ML pipeline extraction** — Port model architecture and inference from notebook into `backend/ml/` modules. Validate with CLI smoke test on `sample_session.csv` before wiring to FastAPI.
3. **Session upload pipeline** — Upload endpoint with CSV validation, stub ML call first (to lock the interface contract), then replace stub with real ML modules. Session + exercise_log storage. Session history and detail endpoints.
4. **Analytics endpoints** — Aggregated stats for dashboard, cross-session exercise progress queries.
5. **LLM integration** — Gemini service, prompt builder, caching layer, analyze endpoint.
6. **React frontend** — Build page by page in route order: Landing → Auth → Dashboard → Upload → Summary → AI Analysis → Analytics → History.
7. **Testing** — pytest for ML pipeline (deterministic), auth flow, CSV validation edge cases. Security review pass (CORS, rate limiting on auth endpoints, JWT expiry).
8. **Dockerization + deployment** — Dockerfile, docker-compose, Nginx config, EC2 setup, Vercel deploy, DuckDNS + Let's Encrypt SSL.

---

## Architectural Rules (Enforce Throughout)

- ML pipeline modules must have zero FastAPI imports — they are pure Python functions callable from CLI, tests, or any web framework
- Upload pipeline is synchronous for v1 — no Celery/Redis task queue (note this as a future scaling improvement in README)
- Gemini API is cached per session — never re-call on page refresh
- Authorization check on every data endpoint: filter by `user_id` from JWT, never from request body
- Calorie values always labeled "estimated" in UI and API responses
- Rep counts always labeled "estimated" in UI — note peak detection accuracy varies by exercise
- Refresh tokens are DB-whitelisted (hashed), enabling logout/revocation

---

## Known Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Wrist-only model limits generalization | Document v1 supports wrist CSVs only; sample file demonstrates expected format |
| `Null` class dominates predictions | Filter Null in postprocess; never show in summary |
| Rep counts inaccurate on some exercises | Tune peak params per exercise family; label "estimated" in UI |
| No calorie ground truth | MET heuristic; labeled "estimated" throughout |
| EC2 CPU inference slow | Batch all windows in one forward pass; note ONNX/TorchScript as future optimization |
| Gemini API cost/rate limits | Cache per session; never call on re-renders |

---

## Deliverables Expected from Claude Code at Each Step

- Propose file/folder structure before generating code for any new module
- Briefly explain where each new piece fits in the overall architecture
- After each module: provide a curl command or CLI command to validate it works
- Dockerfiles + docker-compose for local dev; deployment notes when relevant
- Tests for all ML pipeline modules and auth flow (pytest)
- Security review pass before deployment phase