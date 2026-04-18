# Matrix Quote Web

Full-stack web application that wraps the Matrix per-operation Gradient Boosting quoting engine from `matrix_quote_app/`. Customer-facing single-quote estimator (with a batch upload shell — inference not yet wired) plus a password-protected admin console for training and data exploration. Supports a persistent light/dark theme toggle.

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
│       ├── explain.py          # per-quote driver contributions + neighbor search
│       ├── pdf.py              # render_quote_pdf() — WeasyPrint/Jinja PDF renderer
│       ├── quotes_storage.py   # saved-quote CRUD, atomic-replace parquet persistence
│       ├── templates/          # Jinja2 PDF template + print CSS + SVG wordmark
│       └── routes/
│           ├── quote.py        # /api/quote/single + /api/quote/pdf (ad-hoc PDF)
│           ├── quotes.py       # /api/quotes CRUD + duplicate + per-scenario PDF
│           ├── metrics.py      # /api/metrics/* — headline + history + calibration + GET /api/demo/status
│           ├── insights.py     # /api/insights/overview — executive KPI snapshot
│           └── admin.py        # admin-guarded routes incl. POST /api/admin/demo/load
├── frontend/        # Vite SPA (Barlow Condensed + JetBrains Mono + Inter; ink/paper/teal/amber design system; light/dark overlay)
├── demo_assets/     # committed synthetic dataset + pretrained models for demo mode
│   ├── data/master/projects_master.parquet  # 300-row synthetic master
│   └── models/     # 12 *.joblib bundles, metrics_summary.csv, metrics_history.parquet, calibration.parquet
├── scripts/         # one-off utilities
│   ├── build_test_fixtures.py   # generate synthetic fixture models (run once)
│   └── generate_demo_assets.py  # rebuild demo_assets/ after schema or pipeline changes
├── tests/           # pytest
│   └── fixtures/tiny_models/   # checked-in synthetic models for unit tests
├── data/master/     # runtime: master parquet + saved quotes parquet (gitignored)
│   └── quotes.parquet          # persisted saved scenarios (atomic-replace writes)
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

### Saved-quotes API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/quotes` | List saved scenarios (filters: `project`, `industry`, `search`, `limit`, `offset`) |
| `POST` | `/api/quotes` | Persist a new scenario (`SavedQuoteCreate` body) |
| `GET` | `/api/quotes/{id}` | Full scenario detail (`SavedQuote`) |
| `DELETE` | `/api/quotes/{id}` | Remove a scenario (204) |
| `POST` | `/api/quotes/{id}/duplicate` | Clone a scenario under a new id (201) |
| `GET` | `/api/quotes/{id}/pdf` | Download a saved scenario as a PDF file |
| `POST` | `/api/quote/pdf` | Download an unsaved cockpit result as a PDF (`AdHocPdfRequest` body) |

### Metrics and Insights API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/metrics` | Per-operation model metrics summary (`MetricsSummary`) |
| `GET` | `/api/metrics/history` | Per-run training history (`TrainingRunRow[]`); returns `[]` until training pipeline persists `metrics_history.parquet` |
| `GET` | `/api/metrics/calibration` | Prediction-vs-actual scatter points (`CalibrationPoint[]`); returns `[]` until `calibration.parquet` exists |
| `GET` | `/api/metrics/headline` | Single-row performance summary (`PerformanceHeadline`); fields are `null` when optional parquet files are absent |
| `GET` | `/api/insights/overview` | Executive KPI snapshot (`InsightsOverview`): active quotes, model readiness, MAPE, calibration band %, 26-week activity chart, latest 5 quotes, MAPE heatmap |
| `GET` | `/api/demo/status` | Demo mode state (`DemoStatus`): `is_demo`, `enabled_env`, `has_real_data`; public endpoint polled by the `DemoChip` component |
| `POST` | `/api/admin/demo/load` | Admin-guarded: copies `demo_assets/` into `DATA_DIR` and writes `status.json`; returns `DemoLoadResponse`; refuses if real data is already present |

No auth gate on quotes endpoints. `created_by` is a browser-captured display name (stored in `localStorage`) sent with each save.

Scenarios are persisted in `data/master/quotes.parquet`. The `inputs` and `prediction` fields are stored as JSON strings so schema evolution of `QuoteInput` does not churn the parquet schema. Writes use an atomic `os.replace` pattern (write to `quotes.parquet.tmp`, then rename).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` to `http://localhost:8000`.

#### Dark mode

The app ships a CSS overlay at `frontend/src/styles/dark-mode.css` (imported in `main.tsx`). Dark mode activates by setting `data-theme="dark"` on the root `<html>` element. No Tailwind `dark:` class variants are used — the overlay remaps `.bg-paper`, `.card`, `.text-ink`, sidebar tokens, inputs, and shadows directly.

A floating `ThemeToggle` pill (bottom-left of every page, rendered once in `Layout.tsx`) toggles between LIGHT and DARK. The user's choice is persisted in `localStorage` under the key `matrix-theme` and restored on next load.

#### Tailwind design tokens

The active token palette is defined in `frontend/tailwind.config.ts` (note: `.ts`, not `.js` — the `.js` artifact in the same directory is a build output and is gitignored from config tracking). The current color families are:

| Family | Purpose |
|--------|---------|
| `ink`, `ink2` | Primary text / interactive ink |
| `paper`, `surface` | Page and card backgrounds |
| `line`, `line2` | Hairlines and dividers |
| `muted`, `muted2` | Secondary / supporting text |
| `amber`, `amberSoft` | Accent / highlight |
| `teal`, `tealDark`, `tealSoft` | Brand primary |
| `success`, `warning`, `danger` | Semantic states |
| `bg`, `border` | Compat shims for `body`/`border-border` utilities |

The legacy `brand`, `navy`, `steel`, and `accent` color families were removed as part of the Plan 7 redesign. Any historical code or PR comments referencing those names should map to the table above: `bg-brand` → `bg-teal`, `bg-navy-900` → `bg-ink`, `bg-steel-100` → `bg-paper`, `text-accent` → `text-teal`.

#### PDF template

The WeasyPrint PDF template lives in `backend/app/templates/`. The Jinja variables the template expects are:

| Variable | Type | Description |
|----------|------|-------------|
| `quote` | `SavedQuote` / `AdHocPdfRequest` | Full quote object (project name, client name, prediction, created_by) |
| `quote_number` | `str` | Human-readable quote identifier |
| `prepared_on` | `str` | Formatted date string |
| `input_rows` | `list[tuple[str, str]]` | Label/value pairs for the input summary table |

`format_hours` and `humanize_bucket` are injected into the Jinja environment by `_render_env` in `backend/app/pdf.py` — they are not passed as template variables.

The template renders in the Matrix ink (`#0D1B2A`) + amber (`#F2B61F`) + teal (`#1F8FA6`) + hairline (`#E5E1D8`) palette. Page 1 has a 3pt ink top band followed by a 1.5pt amber band. Numeric cells use JetBrains Mono with `font-variant-numeric: tabular-nums`. The confidence range label reads "90% CI".

### Demo mode

Set `ENABLE_DEMO=1` with an empty `DATA_DIR` to seed a synthetic dataset + pretrained models at startup:

    ENABLE_DEMO=1 DATA_DIR=./.tmp_demo uvicorn backend.app.main:app

Admins can also load demo data at runtime via the "Load demo data" button on Upload & Train. The demo load refuses when real data is already present. A "Demo mode" chip renders in the top-right of every page while demo data is loaded.

Rebuild demo assets with:

    python scripts/generate_demo_assets.py

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

The production image installs `libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libharfbuzz0b fonts-liberation` at build time so WeasyPrint can render PDFs. These libraries are absent on Windows dev boxes; `pdf.py` uses a lazy `from weasyprint import HTML` inside the render function so the module imports cleanly locally — the `OSError` only surfaces at render time (i.e. only if you actually call the PDF endpoint without the native libs installed).

First-use checklist in production: sign in at `/admin/login`, upload a project-hours xlsx on `/admin/train`, wait for the 12 operation models to train. After training completes the `/` Single Quote page becomes usable.

### Single Quote cockpit

The Single Quote page (`/`) uses a two-column CSS-grid workspace on `≥lg` viewports: the quote form on the left, a sticky result panel on the right. On mobile the form stacks above the result. The page header carries the eyebrow `"Estimate · Cockpit"`. The result panel contains:

- **HeroEstimate** — count-up animation, amber accent stripe, p10–p90 CI rail, and a 5-pip confidence indicator labeled Weak / Moderate / Strong / Very Strong. A mono `model · current · N ops` strip runs below the hero.
- **Estimate tab** — per-bucket breakdown with eyebrow operation codes (ME / EE / CON / …), ink bars, and a Hours / % mode toggle.
- **Drivers tab** — bidirectional amber/teal bars radiating from a center axis with a legend.
- **Similar tab** — neighbor projects with teal similarity pips and signed amber/teal Δ values.
- **Scenarios tab** — saved quotes for the current session; the active scenario is ringed in teal, and each row has an outlined Compare pill.

Press `⌘/Ctrl+Enter` from anywhere on the page to submit the form; the submit button is labeled "Regenerate estimate". The form submit bar is solid ink with an amber `↵` / `⌘↵` hint.

**Save flow:** the outlined "Save" button in the result panel prompts for a name and project name, then calls `POST /api/quotes` and toasts on success. The `created_by` field is populated from the browser display name captured via `frontend/src/lib/displayName.ts` (stored in `localStorage`; the user is prompted once on first save). The Compare pill in ScenariosTab navigates to `/quotes` where saved scenarios can be bulk-selected.

**Export PDF (ad-hoc):** the solid-teal "Export" button in the result panel prompts for a project name, then calls `POST /api/quote/pdf` and triggers a browser download — no save required. The PDF is a 3-page Matrix-branded document: cover with headline estimate, per-bucket breakdown + input summary, and assumptions/disclaimers. The WeasyPrint template renders in the Matrix ink/amber/teal palette with JetBrains Mono tabular numerics; see [PDF template](#pdf-template) for details on the Jinja variables.

### Saved Quotes (`/quotes`)

Filterable, searchable list of all persisted scenarios. A 4-card KPI strip at the top shows total saved, last-7-days count, average hours, and high-confidence % (scenarios where the 90% CI band is ≤ 25% of the p50 estimate, marked with an amber top stripe).

Table columns: checkbox, name/project, industry, hours (p50), range (p10–p90), confidence (1–5 amber pips; thresholds: ≤10% CI/hours → 5, ≤20% → 4, ≤35% → 3, ≤55% → 2, else 1), saved-at, hover menu.

Filters: project dropdown, industry dropdown, free-text search. Check 2–3 rows to reveal the ink-colored bulk bar; when exactly 2 or 3 rows are selected an amber "Compare →" link appears — otherwise it reads "Pick 2 or 3 to compare". Per-row hover menu: Duplicate, Export PDF, Delete. The PDF action calls `GET /api/quotes/{id}/pdf` and triggers a browser download.

### Compare (`/quotes/compare?ids=a,b[,c]`)

Side-by-side view for 2–3 saved scenarios. The first scenario is the anchor (amber left-rail + "Anchor" eyebrow); all deltas are measured against it.

- **Header:** display-hero hours, 90% CI range, and signed Δ vs anchor for each non-anchor column. Positive deltas (more hours) render in amber; negative deltas (fewer hours) render in teal.
- **Per-bucket chart:** grouped bar chart of operation-bucket hours across all scenarios (Recharts, ink/amber/teal palette, JetBrains Mono axis labels).
- **Input diff:** grid showing only fields that differ; non-anchor changed cells are colored `text-amber`.
- **Drivers strip:** 3-col split with amber "Anchor · top drivers" eyebrow (placeholder until per-saved-quote drivers are persisted in a follow-up).

### Executive Overview (`/insights`)

Four KPI cards rendered with display-hero numerics (Barlow Condensed, large weight): Active Quotes, Model Readiness, Overall MAPE, and Confidence Calibration. The Overall MAPE and Confidence Calibration cards carry an amber left-border stripe to draw attention to the accuracy signals. Below the cards, a `QuotesActivityChart` renders 26 weeks of quote volume as ink-filled bars with the current week highlighted in amber. A `LatestQuotesTable` shows the five most recent saved quotes in a grid-row layout with mono tnum columns for hours and range. An `AccuracyHeatmap` presents per-operation MAPE in a teal-tint ramp (low error = light teal, high error = deep teal) with mono axis labels. Each visual group is introduced by an eyebrow section label (small-caps, spaced tracking).

### Estimate Accuracy (`/performance`)

`HeadlineKPIs` repeats the Overall MAPE card with its amber stripe alongside Calibration Band %. `MapeByOperation` renders per-operation MAPE as a horizontal bar chart in ink with mono axis labels — the bar fill is uniform ink, not color-coded, so the length alone encodes magnitude. `CalibrationScatter` plots predicted-vs-actual hours as a scatter with a `y=x` reference line (dashed amber); dots above the line are teal (over-estimate) and dots below are rose/danger (under-estimate). `TrainingHistoryChart` shows MAPE over training runs as a teal line chart with an amber hover dot; its eyebrow reads "MAPE · over time" (not "Training history", which is reserved for the outer section label). All four charts share a common `chartTheme.ts` that exports palette constants and axis defaults to keep the two dashboards visually consistent.

### Frontend routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | `SingleQuote` | Two-column estimator cockpit |
| `/batch` | `BatchQuotes` | Upload shell: dropzone, CSV schema reference panel, and placeholder recent-batches list (`BatchDropzone`, `BatchSchemaRef`, `BatchRecentList`). Drop/select toasts a stub message; no batch inference endpoint is wired yet. |
| `/quotes` | `Quotes` | Saved scenarios list |
| `/quotes/compare` | `Compare` | Side-by-side scenario comparison |
| `/performance` | `ModelPerformance` | Estimate accuracy dashboard |
| `/insights` | `ExecutiveOverview` | Executive KPI overview (activity chart, MAPE heatmap) |
| `/admin/login` | `AdminLogin` | Auth gate — amber top stripe, teal "Admin · access" eyebrow, ink submit button. Fully functional. |
| `/admin` | `AdminOverview` | 4 KPI cards (Models ready, Training rows, API uptime 30d, Open flags), training runs table, system alerts list, data sources table. "Models ready" is live; remaining cards and tables are sample data until the admin dataset endpoint ships. |
| `/admin/train` | `AdminTrain` | Real "Load demo data" mutation card (teal stripe, `Sparkles` icon) wrapped in a visual shell: 4-step progress rail (Upload → Validate → Train → Review), dashed upload placeholder, config panel. |
| `/admin/data` | `AdminData` | Filter bar + summary stats row + histogram shell (SVG bars, amber middle buckets, ink flanks) + data table placeholder. Sample data from fixtures. |
| `/admin/drivers` | `AdminDrivers` | Operation picker + global feature importance bar chart + SVG partial-dependence chart + neighbor pool config card. Sample data from fixtures. |

Sample data for admin shells is sourced from `frontend/src/pages/admin/fixtures.ts`, which exports `SAMPLE_RUNS`, `SAMPLE_ALERTS`, `SAMPLE_SOURCES`, `SAMPLE_IMPORTANCE`, and `SAMPLE_HISTOGRAM` arrays typed against `TrainingRun`, `AdminAlert`, `DataSource`, `FeatureImportance`, and histogram bucket interfaces. Each card header labels its content "sample data" so the placeholder state is visually explicit.

Compare-PDF (multi-scenario) is deferred per spec; only single-quote PDFs are supported.
