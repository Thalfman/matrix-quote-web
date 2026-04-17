# Matrix Quote Web

Full-stack web application that wraps the Matrix per-operation Gradient Boosting quoting engine from `matrix_quote_app/`. Customer-facing single/batch quote estimator plus a password-protected admin console for training and data exploration.

## Stack

- **Backend:** FastAPI (Python 3.11) wrapping `core/` + `service/` vendored from `matrix_quote_app/` without modification.
- **Frontend:** Vite + React 18 + TypeScript, Tailwind CSS, TanStack Query, React Router, Recharts.
- **Deployment:** Railway (single service) with a persistent volume mounted at `/data`.

## Project layout

```
matrix-quote-web/
├── core/            # vendored ML library — DO NOT EDIT
├── service/         # vendored prediction orchestration — DO NOT EDIT
├── backend/         # FastAPI wrapper
│   └── app/
│       └── explain.py   # per-quote driver contributions + neighbor search
├── frontend/        # Vite SPA (Inter font, Matrix navy/electric-blue palette)
├── scripts/         # one-off utilities
│   └── build_test_fixtures.py   # generate synthetic fixture models (run once)
├── tests/           # pytest
│   └── fixtures/tiny_models/   # checked-in synthetic models for unit tests
├── data/master/     # runtime: master parquet + upload log (gitignored)
├── models/          # runtime: trained joblib bundles + metrics_summary.csv (gitignored)
├── Dockerfile
├── railway.json
└── requirements.txt # production deps
```

The `core/` and `service/` modules are treated as a vendored library. Changes should be made upstream in `matrix_quote_app/` and synced over — never edited in place.

## Local development

### Backend

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`.

`POST /api/quote/single` returns `ExplainedQuoteResponse`: the prediction is
nested under `body.prediction` (not top-level), and `body.drivers` /
`body.neighbors` carry per-quote explainability data. Both explain fields
degrade gracefully to `null` if models don't support SHAP.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to `http://localhost:8000`.

## Running tests

Backend tests depend on a checked-in fixture bundle of tiny synthetic models in
`tests/fixtures/tiny_models/`. The bundle is already committed; you only need to
regenerate it if the training pipeline changes:

```bash
python scripts/build_test_fixtures.py   # re-generates parquet + joblib files
```

Tests that need the models set `DATA_DIR` via `monkeypatch` automatically; no
env var is required when running `pytest` normally.

```bash
pytest
cd frontend && npm test
```

## Deployment (Railway)

1. Connect the GitHub repo to a new Railway project.
2. Attach a Volume to the service at `/data` (1 GB is plenty for this app).
3. Set env vars: `ADMIN_PASSWORD`, `ADMIN_JWT_SECRET`, `DATA_DIR=/data`.
4. Deploy — the Dockerfile builds the frontend and serves it alongside the API.

First-use checklist in production: sign in at `/admin/login`, upload a project-hours xlsx on `/admin/train`, wait for the 12 operation models to train. After training completes the `/` Single Quote page becomes usable.

### Single Quote cockpit

The Single Quote page (`/`) uses a two-column CSS-grid workspace on `≥lg` viewports: the quote form on the left, a sticky result panel on the right. On mobile the form stacks above the result. The result panel contains a hero estimate (count-up animation, 5-dot confidence indicator) plus four tabs — Estimate (per-bucket breakdown), Drivers (signed SHAP contributions), Similar (neighbor projects with Δ), and Scenarios (session-only saved quotes). Press `⌘/Ctrl+Enter` from anywhere on the page to submit the form. Scenario persistence and PDF export land in Plans C and D respectively.
