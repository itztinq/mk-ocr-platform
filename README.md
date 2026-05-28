# Macedonian OCR Platform

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19.x-61DAFB?logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8.x-646CFF?logo=vite&logoColor=white)
![Tesseract](https://img.shields.io/badge/Tesseract-OCR-3B3B3B?logo=tesseract&logoColor=white)

**OCR platform for Macedonian book pages.** Upload scanned images, run OCR with preprocessing, review and correct text, and export cleaned results.

## Overview
Macedonian OCR Platform turns scanned book/document pages into editable text while keeping the review process simple. It is built for teams and individuals digitizing Macedonian-language archives, books, and printed documents that need careful human correction after OCR.

The backend focuses on reliable preprocessing, OCR extraction, and filesystem-based outputs. The frontend provides a bilingual (EN/MK) review interface with per-page navigation, correction tools, and download options. The goal is practical, repeatable digitization without complex infrastructure.

## Core Features
### OCR Processing
- **Batch OCR jobs** — Upload multiple pages and process them in a background task with job progress.
- **Image preprocessing** — Adaptive thresholding and denoising before OCR to improve recognition.
- **Confidence signals** — Average confidence and suspicious token detection from Tesseract data.

### Text Correction
- **Tabbed text views** — Switch between raw, cleaned, and corrected text per page.
- **Inline corrections** — Edit and save corrected text back to the server.
- **Page status tracking** — Mark pages as pending, in review, or done.

### Export System
- **Per-page outputs** — Raw and cleaned OCR files per page.
- **Book-level outputs** — Aggregated raw OCR and corrected book files.
- **Manual export** — Export the best available text per page into a single file.

### UI/UX
- **Bilingual UI** — English and Macedonian localization.
- **Light/Dark themes** — Theme toggle persisted in local storage.
- **Keyboard navigation** — Arrow key navigation between pages in the editor.

### File Management
- **Strict naming format** — Enforces `page_001.jpg` style filenames.
- **Static image serving** — Uploaded images are served from `/images/...`.

## Architecture
The system is split into a React frontend and a FastAPI backend. OCR runs server-side, while the frontend polls job status and drives the correction workflow.

```
React (Vite UI)
      ↓
FastAPI API + Static /images
      ↓
Image Preprocessing (OpenCV)
      ↓
Tesseract OCR (mkd)
      ↓
Text Cleanup + Confidence Scoring
      ↓
Filesystem Outputs (raw/cleaned/corrected/export)
```

**Job handling:** `/ocr/batch-upload` creates an in-memory job and processes pages in a `BackgroundTasks` loop. Progress is polled from the frontend every 1.5s.

## Tech Stack
| Layer | Technology | Purpose |
| --- | --- | --- |
| Language | Python 3 | Backend services and OCR processing |
| API | FastAPI + Uvicorn | HTTP API and static file hosting |
| OCR Engine | Tesseract OCR | Text extraction (`mkd` language) |
| Image Processing | OpenCV, Pillow, NumPy | Preprocessing and image handling |
| Frontend | React 19 + Vite | Review and correction UI |
| i18n | i18next | English/Macedonian translations |
| HTTP Client | Axios | Frontend API requests |

## Project Structure
```
backend/                 # FastAPI app (routes, services, schemas)
frontend/                # React + Vite client
ocr_pipeline/            # OCR preprocessing and text cleanup
images/                  # Uploaded page images (runtime output)
ocr_output/              # Raw/cleaned OCR files (runtime output)
text/                    # Corrected text + exports (runtime output)
text_output/_status/     # Page status JSON files (runtime output)
docx/                    # Empty placeholder directory
requirements.txt         # Python dependencies
```

## Installation Guide
### 1) Clone the repository
```bash
git clone https://github.com/itztinq/mk-ocr-platform.git
cd mk-ocr-platform
```

### 2) Set up Python dependencies
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3) Set up the frontend
```bash
cd frontend
npm install
```

### 4) Install Tesseract OCR + Macedonian language pack
> [!NOTE]
> The backend looks for `C:\Program Files\Tesseract-OCR\tesseract.exe` on Windows. On other platforms, ensure `tesseract` is available on your PATH and the `mkd` language data is installed.

**Windows**
- Install Tesseract OCR and ensure the executable matches the path above, or update `ocr_pipeline/ocr_engine.py`.

**Linux**
- Install `tesseract-ocr` and the Macedonian data package (often `tesseract-ocr-mkd`).

**macOS**
- Install Tesseract with your package manager and ensure the `mkd` traineddata is available.

## Running the Application
### Backend (FastAPI)
```bash
uvicorn backend.app.main:app --reload
```

### Frontend (Vite)
```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` for the UI. API docs are available at `http://127.0.0.1:8000/docs`.

> [!TIP]
> Use filenames like `page_001.jpg` and provide a book name. Outputs are stored under `images/`, `ocr_output/`, and `text/`.

## OCR Workflow
1. **Upload images** — Send a book name and multiple `page_###` images to `/ocr/batch-upload`.
2. **Preprocessing** — Images are denoised and adaptively thresholded.
3. **OCR execution** — Tesseract extracts Macedonian text.
4. **Confidence scoring** — Average confidence and suspicious tokens are computed.
5. **Text correction** — The UI loads raw/cleaned text and lets you save corrections.
6. **Export generation** — Book-level raw/corrected and combined exports are written.

## API Documentation
Key endpoints (see `/docs` for full OpenAPI):

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| POST | `/ocr/upload-image` | OCR a single image (multipart) |
| POST | `/ocr/batch-upload` | OCR multiple pages, returns a job |
| GET | `/jobs/{job_id}` | Get job status and progress |
| GET | `/books/{book}/pages` | List pages for a book |
| GET | `/books/{book}/pages/{page}` | Get page detail + text blocks |
| PUT | `/books/{book}/pages/{page}/corrected-text` | Save corrected text |
| PUT | `/books/{book}/pages/{page}/status` | Update page status |
| GET | `/books/{book}/pages/{page}/download/{kind}` | Download raw/cleaned/corrected |
| GET | `/books/{book}/export/txt` | Export best-available text |
| GET | `/files/download/{type}/{filename}` | Download raw/cleaned/corrected file |
| GET | `/files/download/book/{type}/{book}` | Download book-level file |
| POST | `/text/save-corrected` | Save corrected text (alternate payload) |

**Batch upload example**
```bash
curl -X POST http://127.0.0.1:8000/ocr/batch-upload \
  -F "book_name=macedonian-novel" \
  -F "files=@page_001.jpg" \
  -F "files=@page_002.jpg"
```

## Output Files
Outputs are stored on disk for easy inspection and reuse:

- `images/<book>/page_###.<ext>` — Uploaded page images
- `ocr_output/<book>/pages/page_###_raw.txt` — Raw OCR text per page
- `ocr_output/<book>/pages/page_###_cleaned.txt` — Cleaned OCR text per page
- `ocr_output/<book>_ocr_raw.txt` — Aggregated raw OCR text for a book
- `text/<book>/pages/page_###_corrected.txt` — Corrected text per page
- `text/<book>_corrected.txt` — Aggregated corrected text for a book
- `text/<book>/<book>_export.txt` — Export with best available text per page
- `text_output/_status/<book>.json` — Page status map (`pending`/`in_review`/`done`)

## Development Notes
- **Job state is in-memory.** Restarting the backend clears job progress.
- **Status files are JSON.** Page status is persisted in `text_output/_status/`.
- **Tesseract path issues** are the most common setup problem on Windows.
- **Encoding:** All text outputs are UTF-8; keep editors configured accordingly.
- **Performance:** OCR is CPU-bound; large batches will run sequentially.
