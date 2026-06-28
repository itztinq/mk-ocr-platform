# Macedonian OCR Platform

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-6.x-646CFF?logo=vite&logoColor=white)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-3B3B3B?logo=tesseract&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-8-47A248?logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/k3d-5.x-326CE5?logo=kubernetes&logoColor=white)
![Argo CD](https://img.shields.io/badge/Argo_CD-2.x-EF7B4D?logo=argo&logoColor=white)

**OCR platform for Macedonian book pages.** Upload scanned images or PDFs, run OCR with preprocessing, review and correct text, and export cleaned results. Deployed on Kubernetes with a fully automated CI/CD pipeline.

## Core Features

- **Batch OCR** — Upload multiple images or a PDF; pages are OCR'd in background jobs with real-time progress
- **Text correction** — Tabbed raw/cleaned/corrected views with inline saving
- **Bilingual UI** — English and Macedonian with light/dark themes
- **MongoDB persistence** — Job history survives restarts (replaced in-memory storage)
- **Delete history** — Individual job deletion or clear all history
- **Export** — Download per-page or book-level text files

## Architecture

```
Browser ──http://localhost:8080──→ Traefik Ingress
                                       │
                          ┌────────────┼────────────┐
                          │            │            │
                     ┌────┴────┐  ┌───┴────┐  ┌───┴────┐
                     │frontend │  │backend │  │mongodb │
                     │ :80     │  │ :8000  │  │ :27017 │
                     └─────────┘  └───┬────┘  └────────┘
                                      │
                               Tesseract OCR
                               (inside backend pod)
```

All API calls pass through the Ingress:
- `/api/*` → backend (prefix stripped)
- `/images/*` → backend (serves uploaded images)
- `/` → frontend (React SPA)

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI + Uvicorn + Motor (async MongoDB) |
| Database | MongoDB 8 (StatefulSet in K8s) |
| OCR | Tesseract 5 (mkd language) |
| PDF | PyMuPDF (fitz) |
| Image processing | OpenCV, Pillow |
| Frontend | React 19 + Vite + Axios |
| i18n | i18next (English / Macedonian) |
| Container | Docker + Docker Compose |
| Orchestration | Kubernetes (k3d) |
| CI/CD | GitHub Actions + Argo CD |
| Ingress | Traefik (k3s built-in) |

## Project Structure

```
./
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── api/routes/      # Jobs, OCR, Books, Files, Text
│   │   ├── core/            # Config, database (Motor)
│   │   ├── schemas/         # Pydantic models
│   │   └── services/        # Job service, OCR service, Book service
│   └── Dockerfile
├── frontend/                # React + Vite
│   ├── src/
│   │   ├── api/             # Axios client (prefixes /api)
│   │   ├── components/      # UploadSection, JobHistory, ImageViewer, Editor
│   │   └── context/         # AppContext (book state)
│   ├── Dockerfile
│   └── nginx.conf           # Serves static files only (API proxied by Ingress)
├── ocr_pipeline/            # Tesseract preprocessing + text cleanup
├── k8s/                     # Kubernetes manifests
│   ├── namespace.yaml
│   ├── ingress.yaml         # Traefik Ingress (/api + /images → backend, / → frontend)
│   ├── mongodb/             # StatefulSet + Service + ConfigMap + Secret
│   ├── backend/             # Deployment + Service + ConfigMap + PVC
│   ├── frontend/            # Deployment + Service
│   └── argocd/              # Argo CD Application manifest
├── docker-compose.yml       # Dev: mongodb + backend + frontend
├── .github/workflows/ci.yml # CI/CD: build, push to Docker Hub, deploy via Argo CD
├── .env.example             # Environment variable template
└── requirements.txt
```

## Quick Start — Docker Compose

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/mk-ocr-platform.git
cd mk-ocr-platform

# 2. Copy env and edit if needed
cp .env.example .env

# 3. Start all services
docker compose up -d

# 4. Open the app
open http://localhost:5173
```

## Quick Start — Kubernetes (k3d)

### Prerequisites
- [k3d](https://k3d.io/) installed
- Docker Hub account

### 1. Create the cluster

```bash
k3d cluster create mk-ocr --api-port 6550 -p "8080:80@loadbalancer"
```

> Docker images are already available on Docker Hub as `martinnq/mk-ocr-*`.  
> If you forked the repo, build and push your own images first, then update `k8s/*/deployment.yaml`.

### 2. Create the secret files

```bash
cp k8s/mongodb/secret.yaml.example k8s/mongodb/secret.yaml
cp k8s/backend/secret.yaml.example k8s/backend/secret.yaml
# Edit the passwords if desired
```

### 3. Deploy to the cluster

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/mongodb/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify

```bash
kubectl get pods -n mk-ocr-app
# Wait for all pods to be Ready, then:
open http://localhost:8080
```

## CI/CD Pipeline

The `.github/workflows/ci.yml` implements a full CI/CD pipeline.

### CI — Build and Push

Every push to `main` triggers:

1. **backend** job — builds and pushes `mk-ocr-backend` to Docker Hub (`latest` + `sha-*` tags)
2. **frontend** job — builds and pushes `mk-ocr-frontend` to Docker Hub (`latest` + `sha-*` tags)
3. **deploy** job — updates `k8s/*/deployment.yaml` with the new SHA image tag, commits and pushes to Git

### CD — Argo CD GitOps

[Argo CD](https://argo-cd.readthedocs.io/) runs in the cluster and watches the Git repo. When the deploy job pushes updated manifests, Argo CD automatically syncs them to the cluster.

### Setup

1. Add these **GitHub Secrets** (repo → Settings → Secrets → Actions):

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

2. Install Argo CD:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.12.6/manifests/install.yaml
```

3. Configure Argo CD:

```bash
# Edit k8s/argocd/application.yaml — replace YOUR_GITHUB_USERNAME
kubectl apply -f k8s/argocd/application.yaml
```

### Argo CD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 9090:80
# Open https://localhost:9090
# Username: admin
# Password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/ocr/batch-upload` | Upload multiple images, returns a job |
| `POST` | `/ocr/upload-pdf` | Upload PDF, renders pages, queues OCR |
| `GET` | `/jobs/history` | List all jobs |
| `DELETE` | `/jobs/history` | Clear all job history |
| `GET` | `/jobs/{id}` | Get job status + progress |
| `DELETE` | `/jobs/{id}` | Delete a single job |
| `GET` | `/books/{book}/pages` | List pages for a book |
| `GET` | `/books/{book}/pages/{page}` | Get page detail + text blocks |
| `PUT` | `/books/{book}/pages/{page}/corrected-text` | Save corrected text |
| `GET` | `/books/{book}/export/txt` | Export best-available text |

Full OpenAPI docs at `http://localhost:8080/api/docs` (via Ingress) or `http://127.0.0.1:8000/docs` (direct).

## Environment Variables

| Variable | Default | Description |
| --- | --- | --- |
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGODB_DB_NAME` | `mk_ocr_platform` | Database name |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |
| `OCR_LANGUAGE` | `mkd` | Tesseract language |
| `TESSERACT_CMD` | platform-dependent | Path to Tesseract binary |
| `IMAGES_DIR` | `./images` | Image storage directory |
| `OCR_OUTPUT_DIR` | `./ocr_output` | OCR output directory |
| `TEXT_OUTPUT_DIR` | `./text` | Corrected text directory |

## Development Notes

- **MongoDB** is required. For local dev without Docker, set `MONGODB_URI` in `.env` to your local MongoDB instance.
- **Filename format** for batch uploads: `page_001.jpg`, `page_002.png`, etc. (3+ digits).
- **Tesseract** must be installed with the `mkd` language pack.
- **Encoding:** All text outputs are UTF-8.
- **Performance:** OCR is CPU-bound; large batches run sequentially in background tasks.

## License

MIT
