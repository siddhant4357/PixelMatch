---
title: Pixelmatch Api
emoji: 📸
colorFrom: purple
colorTo: pink
sdk: gradio
sdk_version: 4.44.1
app_file: app.py
pinned: false
---

# PixelMatch — AI-Powered Smart Photo Search 📸🤖

**Find every photo you appear in — instantly — using facial recognition and natural language AI.**

Built for events, weddings, conferences, and gatherings. Upload a selfie, ask *"Show my photos from August 2026"*, and get instant, privacy-first results.

<div align="center">

**⚡ Powered by InsightFace + Groq AI • Deployed on Hugging Face Spaces + Vercel ⚡**

🌐 **Live at**: [pixel-match-six.vercel.app](https://pixel-match-six.vercel.app)

</div>

---

## 🧠 Project Overview

PixelMatch is a production-grade AI photo search platform combining two technical pillars:

1. **Super-Ensemble Face Recognition** — InsightFace (buffalo_s) extracts 512-dimensional face embeddings stored in a FAISS vector index. Guests upload one selfie and the system finds every photo they appear in via cosine similarity search.

2. **AI Natural Language Search** — Groq AI (Llama 3) parses conversational queries like *"show me all pics of 2026"* or *"photos from August to September"* and applies date, location, and device filters on top of the face-match results.

> [!NOTE]
> **Core Philosophy**
> *"Deep learning is not about models alone — it is about data, design, and decisions."*
> This project demonstrates practical Transfer Learning for real-world, data-constrained face recognition and production-grade deployment at zero infrastructure cost.

---

## 🏗️ System Architecture

### High-Level Data Flow

```
Admin uploads photos
    → InsightFace detects all faces
    → 512-dim embeddings stored in per-room FAISS index
    → EXIF metadata (GPS, timestamp, device) stored in location DB

Guest joins room with code
    → Uploads selfie
    → Selfie embedding generated (in-memory, never stored)
    → FAISS cosine search finds matching photos
    → Optional: AI query filters by date / location / device
```

### A. Face Recognition Pipeline (InsightFace buffalo_s)

| Stage | Detail |
|---|---|
| **Detection** | RetinaFace (det_500m.onnx) — detects faces in group shots |
| **Landmarks** | 2D-106 & 3D-68 landmark detection for alignment |
| **Embedding** | w600k_mbf.onnx — 512-dim recognition embedding |
| **Search** | FAISS flat inner-product index, threshold 0.50 |
| **Accuracy** | ~99%+ on front-facing photos |

### B. AI Natural Language Understanding (Groq)

- **Model**: `llama3-70b-8192` (configurable via `AI_MODEL` env var)
- **Query types supported**:
  - Year-only: *"show me all pics of 2026"* → `2026-01-01` to `2026-12-31`
  - Year range: *"photos from 2025 to 2026"* → full range filter
  - Month+Year: *"August 2026 photos"* → exact month range
  - Month-only: *"January photos"* → matches across all years
  - Location: *"photos from Jaisalmer"* → GPS haversine + name match
  - Device: *"iPhone photos"* → EXIF camera make filter
  - Show all: *"show all my photos"* → bypasses all filters

### C. Room-Based Multi-Event Architecture

Each event lives in an isolated room with:
- Separate FAISS index at `data/rooms/{ROOM_CODE}/chromadb/`
- Separate location DB at `data/rooms/{ROOM_CODE}/location_db.json`
- Per-room consent tracking
- 6-character alphanumeric room codes

---

## 🚀 Key Features

- **🏠 Multi-Room Event Management** — Create or join event rooms with 6-digit codes. Each room has fully isolated photo storage and face indexes.
- **🤖 InsightFace Recognition** — buffalo_s model preloaded at startup for fast inference on CPU (no GPU required).
- **💬 AI Conversational Search** — Ask in natural language by year, month range, location, or device. Powered by Groq Llama 3.
- **📅 Smart Date Filtering** — Year-only, year-range, month-only, and full date-range queries all handled correctly.
- **📍 GPS Metadata Extraction** — EXIF GPS coordinates extracted and reverse-geocoded (offline via `reverse_geocoder`) for location-based search.
- **📦 Download All as ZIP** — One-click download of all matched photos as a ZIP archive.
- **🔒 Privacy-First** — Selfie embeddings are generated in-memory and never written to disk. Guests only see photos they appear in. Data auto-expires after 7 days.
- **📱 Fully Mobile-Friendly** — Responsive UI with hamburger nav, stacking layouts, and touch-friendly controls.
- **✨ Glassmorphic UI** — Warm peach/purple design system with backdrop-blur cards, purple→pink gradients, and smooth transitions.

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Web Framework | FastAPI (Python 3.10) |
| Face Detection + Recognition | InsightFace buffalo_s (ONNX, CPUExecutionProvider) |
| Vector Search | FAISS flat index (512-dim cosine) |
| AI Query Parsing | Groq AI — `llama3-70b-8192` |
| EXIF Metadata | Pillow (GPS fix: `float()` cast on IFDRational) |
| Reverse Geocoding | `reverse_geocoder` (offline) + geopy (online fallback) |
| Auth | Clerk (JWT verification on protected endpoints) |
| Database | SQLAlchemy async (SQLite locally, PostgreSQL in prod) |
| HF Spaces Compat | Dummy Gradio watchdog on port 7861; FastAPI on port 7860 |

### Frontend
| Layer | Technology |
|---|---|
| Framework | React 18 + Vite |
| Styling | Tailwind CSS v4 |
| Auth | Clerk React (`@clerk/clerk-react`) |
| Routing | React Router v6 |
| Icons | Lucide React |
| HTTP | Axios (with Clerk JWT injection) |

### Infrastructure
| Service | Purpose |
|---|---|
| Hugging Face Spaces | Backend API hosting (free CPU tier) |
| Vercel | Frontend hosting (auto-deploy from GitHub) |
| GitHub | Source of truth — both HF and Vercel deploy from `main` |

---

## 🚀 Local Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- 2GB+ free disk (InsightFace downloads ~125MB model on first run)

### 1. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your keys (see below)

python main.py
# Runs on http://localhost:7860
```

### 2. Frontend

```bash
cd frontend
npm install

# Configure environment
echo "VITE_API_URL=http://localhost:7860" > .env
echo "VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here" >> .env

npm run dev
# Runs on http://localhost:5173
```

---

## ⚙️ Environment Variables

### Backend `.env`

```env
# Groq AI
GROQ_API_KEY=your_groq_api_key_here
AI_MODEL=llama3-70b-8192

# Auth (Clerk)
CLERK_SECRET_KEY=sk_test_your_key_here

# Database (optional — disables DB if not set)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# CORS
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173

# Storage (optional — uses local disk if not set)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=

# Limits
MAX_UPLOAD_SIZE_MB=10
SIMILARITY_THRESHOLD=0.50
MIN_FACE_CONFIDENCE=0.60
SESSION_TIMEOUT_MINUTES=30
```

### Frontend `.env`

```env
VITE_API_URL=https://sid4357-pixelmatch-api.hf.space
VITE_CLERK_PUBLISHABLE_KEY=pk_live_your_key_here
```

---

## 📦 Deployment

### Backend → Hugging Face Spaces

The repo root contains `app.py` which:
1. Launches a dummy Gradio block on port 7861 (satisfies HF watchdog)
2. Starts the FastAPI app via `uvicorn` on port 7860 (the public port)

Push to `huggingface` remote to deploy:
```bash
git push huggingface main
```

Set these in HF Spaces **Secrets**:
- `GROQ_API_KEY`
- `CLERK_SECRET_KEY`
- `ALLOWED_ORIGINS`
- `DATABASE_URL` (optional)
- `AI_MODEL=llama3-70b-8192`

### Frontend → Vercel

Vercel auto-deploys on push to `main` on GitHub.

Set in Vercel **Environment Variables**:
- `VITE_API_URL=https://sid4357-pixelmatch-api.hf.space`
- `VITE_CLERK_PUBLISHABLE_KEY=pk_live_...`

---

## 📁 Project Structure

```
PixelMatch/
├── app.py                        # HF Spaces entry: Gradio watchdog + uvicorn launcher
├── Dockerfile                    # Container build (for local Docker or custom deploy)
├── backend/
│   ├── main.py                   # FastAPI app — all API endpoints
│   ├── requirements.txt
│   ├── .env                      # Local secrets (never committed)
│   ├── models/
│   │   ├── face_recognition.py   # InsightFace buffalo_s wrapper
│   │   ├── vector_db.py          # FAISS per-room index manager
│   │   └── location_db.py        # EXIF metadata + GPS storage
│   ├── services/
│   │   ├── admin_service.py      # Bulk photo upload + face indexing pipeline
│   │   ├── ai_search_service.py  # Groq query parser + multi-mode search
│   │   ├── privacy_service.py    # Consent + data lifecycle management
│   │   └── storage_service.py    # S3-compatible cloud storage (optional)
│   └── utils/
│       ├── exif_extractor.py     # GPS IFDRational→float fix, EXIF parsing
│       └── image_processor.py    # Image load/resize helpers
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Routes + Clerk provider + layout wrappers
│   │   ├── index.css             # Tailwind base + no-scrollbar utility
│   │   ├── pages/
│   │   │   ├── Welcome.jsx       # Landing page (warm peach design, mobile-first)
│   │   │   ├── Dashboard.jsx     # "Your Events" — create/join rooms
│   │   │   ├── RoomPage.jsx      # Per-room guest + admin tabs
│   │   │   ├── AskAI.jsx         # Conversational AI search interface
│   │   │   ├── Onboarding.jsx    # First-time selfie upload
│   │   │   ├── Settings.jsx      # Account settings
│   │   │   ├── AuthPage.jsx      # Clerk sign-in/sign-up wrapper
│   │   │   └── Guest.jsx         # Legacy guest portal (standalone)
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Responsive nav with mobile hamburger menu
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── ProgressLoader.jsx
│   │   │   └── SuccessModal.jsx
│   │   └── services/
│   │       └── api.js            # Axios wrapper with Clerk JWT injection
│   └── package.json
└── README.md
```

---

## 📝 Core API Endpoints

### Auth
- `POST /auth/upload-selfie` — Upload selfie, generate embedding, store for user
- `GET /auth/profile` — Get user profile + embedding status

### Rooms
- `POST /rooms/create` — Create a new event room
- `POST /rooms/join` — Join a room by code
- `GET /rooms/my-rooms` — List all rooms user has joined
- `GET /rooms/{room_code}` — Get room details + photo count

### Admin (per-room)
- `POST /admin/upload` — Bulk upload photos for a room (triggers face indexing)

### Guest Search
- `POST /search` — Face similarity search within a room
- `GET /photos/{room_code}/{filename}` — Serve a photo file
- `POST /download-zip` — Download matched photos as ZIP

### AI Search
- `POST /ai/query` — Natural language query (date, location, device filters)

### Consent
- `GET /consent/{room_code}` — Check if user has granted consent for a room
- `POST /consent/{room_code}` — Grant facial recognition consent for a room

---

## 🐛 Known Issues & Troubleshooting

### Pillow GPS Fraction Error
**Symptom**: `TypeError: unsupported format string passed to Fraction.__format__`  
**Cause**: Pillow returns `IFDRational` (a `Fraction` subclass) for GPS EXIF values. Formatting with `:.4f` fails.  
**Fix**: Cast each GPS component to `float()` before arithmetic in `exif_extractor.py` ✅ (fixed)

### HF Spaces Watchdog Crash
**Symptom**: `No @spaces.GPU function detected during startup`  
**Cause**: HF Spaces 0.51+ kills processes that don't call `gr.launch()`.  
**Fix**: `app.py` launches a minimal Gradio block on port 7861 to satisfy the watchdog ✅ (fixed)

### Groq Model Not Found
**Symptom**: `model llama-3.3-70b-versatile does not exist`  
**Fix**: Default model changed to `llama3-70b-8192`. Override with `AI_MODEL` env var ✅ (fixed)

### AI Query Returns No Results
**Symptom**: `"show me all pics of 2026"` → "No photos found"  
**Cause**: Year-only queries weren't producing date ranges; `show_all` wasn't short-circuiting filters; `_simple_parse_query` was missing its `return` statement.  
**Fix**: All three issues patched ✅ (fixed)

---

## 🔒 Privacy & Security

1. **Selfie embeddings** are generated in-memory and never written to disk
2. **Per-room consent** must be granted before facial search is performed
3. **Access isolation** — guests can only see photos from rooms they've joined and consented to
4. **Session timeout** — sessions auto-expire after 30 minutes
5. **Auth** — all protected endpoints require valid Clerk JWT tokens

---

## 📜 License

Licensed under the **MIT License**. Free for educational, academic, and personal use.

**Acknowledgements**: InsightFace (deepinsight), FAISS (Meta AI Research), Groq AI, Clerk.dev, Pillow, FastAPI, React, Vite, Tailwind CSS.

---

<div align="center">

**🎉 Built with ❤️ — find your memories instantly with PixelMatch 🎉**

</div>
