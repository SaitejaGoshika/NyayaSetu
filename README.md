# NyayaSetu

NyayaSetu is a local-first legal workspace for Indian SMEs and the public. It uses Next.js, FastAPI, SQLite, and local disk storage. It does not require Firebase or a paid cloud account. Rule-based contract findings are screening signals, not legal conclusions.

The workspace includes a contract scanner, a secure document vault, a case-preparation desk, a hearing and mediation readiness checklist, and a searchable introductory library of Indian central Acts and public legal-service links. The case desk turns a user's in-browser notes into a matter-specific document checklist and questions to discuss with an advocate. The readiness checklist can be downloaded or printed locally. Notes and checklist state are not sent to the API or saved by the page. The library links readers to India Code and official court/legal-help services; summaries are educational and may not reflect amendments or local rules. The project also includes a YAML-driven rule registry, a synthetic evaluation harness, OCR fallback for scanned PDFs, and an MSME delayed-payment estimator for quick screening checks.

## Requirements

- Node.js 20.9 or newer and npm
- Python 3.10 or newer
- A trusted, locally provisioned scikit-learn model artifact for optional statistical case estimates

## Run the frontend

Start the backend and frontend in separate terminals from the project root:

Backend terminal:

```powershell
python -m uvicorn backend.main:app --reload --reload-dir backend --env-file backend/.env
```

Frontend terminal:

```powershell
npm install
npm run dev
```

Open the application at `http://localhost:3000`. The backend API runs separately at `http://localhost:8000`; its root URL returns a JSON API status response. The frontend defaults to `http://localhost:8000` for API requests. Override `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` only if you run the API elsewhere.

## Run the backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
if (-not (Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
uvicorn backend.main:app --reload --reload-dir backend --env-file backend/.env
```
The backend runs with automatic reloading. `--reload-dir backend` limits watched files to backend source code.

Local accounts use email and password. Password hashes and document metadata live in `backend/data/nyayasetu.db`; uploaded documents live under `backend/data/uploads`. The API sets an HttpOnly session cookie. No Firebase keys or email verification are needed. `JWT_SECRET_KEY` may be left blank for local development; set a random value of at least 32 characters and `NYAYASETU_ENV=production` for a deployment.

## Published judgment reader and case preparation

The Judgment reader scans text in the browser for a limited set of explicit disposition phrases found in published Indian Supreme Court judgments. Pasted text is not sent to the API or saved. It reports phrase matches only; a phrase may occur in a citation or discussion and may not describe the operative order. Verify the signed judgment with a qualified advocate.

The open `labofsahil/Indian-Supreme-Court-Judgments` dataset declares CC-BY-4.0; that declaration and the underlying rights have not been independently verified. An audit of its 42,846 metadata rows found 41,797 non-empty disposition labels but only 653 separate descriptions. The rendered HTML contains post-decision material, so it cannot support a reliable model that predicts outcomes from pre-decision case facts. NyayaSetu does not train or ship an outcome-prediction model from this dataset.

The optional legacy prediction API remains unavailable unless a trusted model artifact is provisioned. It is not used by the Judgment reader and must not be presented as estimating a pending case's result. The Case desk is a separate, browser-only preparation checklist, not an outcome predictor or substitute for an advocate.

## Architecture

- `frontend/app`, `frontend/components`, `frontend/lib`, and `frontend/store`
- `backend/api/routes`, `backend/services`, `backend/models`, and `backend/ml`

Uploads are capped at 10 MiB, type-checked, streamed in chunks to local disk, and associated with the authenticated account in SQLite. The optional model path defaults to `backend/ml/models/case_outcome_model.joblib`; the artifact is intentionally not included.

## Local Storage Limits

SQLite and local disk are suitable for a single-machine development or small single-instance deployment, not horizontally scaled replicas. Data is not encrypted at rest by the app; use full-disk encryption and protected backups. Before public deployment, add HTTPS, CSRF protection for cookie-authenticated writes, login rate limits, malware scanning, retention/deletion workflows, audit logging, monitoring, backups, incident response, and a production-grade database/object store. Set a strong `JWT_SECRET_KEY`; production cookies require HTTPS. Review data-residency obligations and have qualified Indian counsel validate legal rules and model outputs. Predictions are not legal advice and must not be the sole basis for a decision.
